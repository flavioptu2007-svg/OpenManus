import asyncio
import hashlib
import time
from typing import Any, Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, ConfigDict, Field, model_validator
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import config
from app.logger import logger
from app.tool.base import BaseTool, ToolResult
from app.tool.search import (
    BaiduSearchEngine,
    BingSearchEngine,
    DuckDuckGoSearchEngine,
    GoogleSearchEngine,
    WebSearchEngine,
)
from app.tool.search.base import SearchItem
from app.utils.metrics import metrics


class SearchResult(BaseModel):
    """Represents a single search result returned by a search engine."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    position: int = Field(description="Position in search results")
    url: str = Field(description="URL of the search result")
    title: str = Field(default="", description="Title of the search result")
    description: str = Field(
        default="", description="Description or snippet of the search result"
    )
    source: str = Field(description="The search engine that provided this result")
    raw_content: Optional[str] = Field(
        default=None, description="Raw content from the search result page if available"
    )

    def __str__(self) -> str:
        """String representation of a search result."""
        return f"{self.title} ({self.url})"


class SearchMetadata(BaseModel):
    """Metadata about the search operation."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    total_results: int = Field(description="Total number of results found")
    language: str = Field(description="Language code used for the search")
    country: str = Field(description="Country code used for the search")


class SearchResponse(ToolResult):
    """Structured response from the web search tool, inheriting ToolResult."""

    query: str = Field(description="The search query that was executed")
    results: List[SearchResult] = Field(
        default_factory=list, description="List of search results"
    )
    metadata: Optional[SearchMetadata] = Field(
        default=None, description="Metadata about the search"
    )

    @model_validator(mode="after")
    def populate_output(self) -> "SearchResponse":
        """Populate output or error fields based on search results."""
        if self.error:
            return self

        result_text = [f"Search results for '{self.query}':"]

        for i, result in enumerate(self.results, 1):
            # Add title with position number
            title = result.title.strip() or "No title"
            result_text.append(f"\n{i}. {title}")

            # Add URL with proper indentation
            result_text.append(f"   URL: {result.url}")

            # Add description if available
            if result.description.strip():
                result_text.append(f"   Description: {result.description}")

            # Add content preview if available
            if result.raw_content:
                content_preview = result.raw_content[:1000].replace("\n", " ").strip()
                if len(result.raw_content) > 1000:
                    content_preview += "..."
                result_text.append(f"   Content: {content_preview}")

        # Add metadata at the bottom if available
        if self.metadata:
            result_text.extend(
                [
                    f"\nMetadata:",
                    f"- Total results: {self.metadata.total_results}",
                    f"- Language: {self.metadata.language}",
                    f"- Country: {self.metadata.country}",
                ]
            )

        self.output = "\n".join(result_text)
        return self


class SearchCache:
    """TTL cache for search results to avoid repeated queries.

    Caches results keyed by a hash of (query, num_results, lang, country).
    Entries expire after the configured TTL. The cache is bounded to
    prevent unbounded memory growth.

    Attributes:
        ttl_seconds: How long cached entries remain valid (default: 300s = 5 min)
        max_entries: Maximum number of cached queries (default: 100)
    """

    def __init__(self, ttl_seconds: int = 300, max_entries: int = 100):
        self.ttl_seconds = ttl_seconds
        self.max_entries = max_entries
        self._cache: Dict[str, Tuple[float, List[SearchResult]]] = {}
        self._hit_count: int = 0
        self._miss_count: int = 0

    @staticmethod
    def _make_key(query: str, num_results: int, lang: str, country: str) -> str:
        """Generate a deterministic cache key from search parameters."""
        raw = f"{query.strip().lower()}|{num_results}|{lang}|{country}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(
        self, query: str, num_results: int, lang: str, country: str
    ) -> Optional[List[SearchResult]]:
        """Get cached results if available and not expired."""
        key = self._make_key(query, num_results, lang, country)
        entry = self._cache.get(key)

        if entry is None:
            self._miss_count += 1
            return None

        timestamp, results = entry
        if time.monotonic() - timestamp > self.ttl_seconds:
            # Expired
            del self._cache[key]
            self._miss_count += 1
            return None

        self._hit_count += 1
        logger.info(
            f"🔍 Search cache HIT for '{query[:50]}' "
            f"({self._hit_count}/{self._hit_count + self._miss_count} hits)"
        )
        return results

    def set(
        self,
        query: str,
        num_results: int,
        lang: str,
        country: str,
        results: List[SearchResult],
    ) -> None:
        """Store search results in cache."""
        key = self._make_key(query, num_results, lang, country)

        # Evict oldest entry if at capacity
        if len(self._cache) >= self.max_entries:
            oldest_key = min(self._cache, key=lambda k: self._cache[k][0])
            del self._cache[oldest_key]

        self._cache[key] = (time.monotonic(), results)
        logger.info(
            f"🔍 Search cache SET for '{query[:50]}' "
            f"({len(self._cache)}/{self.max_entries} slots used)"
        )

    def invalidate(self, query: Optional[str] = None) -> None:
        """Invalidate cache entries. If query is None, clears entire cache.

        Note: When a query is specified, the entire cache is cleared because
        the hash-based keys include num_results/lang/country, making
        partial invalidation unreliable.
        """
        self._cache.clear()
        if query:
            logger.info(
                f"🔍 Search cache invalidated (all entries) for query '{query[:50]}'"
            )
        else:
            logger.info("🔍 Search cache cleared entirely")

    @property
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics for observability."""
        total = self._hit_count + self._miss_count
        return {
            "size": len(self._cache),
            "max_entries": self.max_entries,
            "ttl_seconds": self.ttl_seconds,
            "hits": self._hit_count,
            "misses": self._miss_count,
            "hit_rate": (
                f"{(self._hit_count / total * 100):.1f}%" if total > 0 else "N/A"
            ),
        }


class WebContentFetcher:
    """Utility class for fetching web content."""

    @staticmethod
    async def fetch_content(url: str, timeout: int = 10) -> Optional[str]:
        """
        Fetch and extract the main content from a webpage.

        Args:
            url: The URL to fetch content from
            timeout: Request timeout in seconds

        Returns:
            Extracted text content or None if fetching fails
        """
        headers = {
            "WebSearch": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        try:
            # Use asyncio to run requests in a thread pool
            response = await asyncio.get_event_loop().run_in_executor(
                None, lambda: requests.get(url, headers=headers, timeout=timeout)
            )

            if response.status_code != 200:
                logger.warning(
                    f"Failed to fetch content from {url}: HTTP {response.status_code}"
                )
                return None

            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")

            # Remove script and style elements
            for script in soup(["script", "style", "header", "footer", "nav"]):
                script.extract()

            # Get text content
            text = soup.get_text(separator="\n", strip=True)

            # Clean up whitespace and limit size (100KB max)
            text = " ".join(text.split())
            return text[:10000] if text else None

        except Exception as e:
            logger.warning(f"Error fetching content from {url}: {e}")
            return None


class WebSearch(BaseTool):
    """Search the web for information using various search engines."""

    name: str = "web_search"
    description: str = """Search the web for real-time information about any topic.
    This tool returns comprehensive search results with relevant information, URLs, titles, and descriptions.
    If the primary search engine fails, it automatically falls back to alternative engines."""
    parameters: dict = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "(required) The search query to submit to the search engine.",
            },
            "num_results": {
                "type": "integer",
                "description": "(optional) The number of search results to return. Default is 5.",
                "default": 5,
            },
            "lang": {
                "type": "string",
                "description": "(optional) Language code for search results (default: en).",
                "default": "en",
            },
            "country": {
                "type": "string",
                "description": "(optional) Country code for search results (default: us).",
                "default": "us",
            },
            "fetch_content": {
                "type": "boolean",
                "description": "(optional) Whether to fetch full content from result pages. Default is false.",
                "default": False,
            },
        },
        "required": ["query"],
    }
    _search_engine: dict[str, WebSearchEngine] = {
        "google": GoogleSearchEngine(),
        "baidu": BaiduSearchEngine(),
        "duckduckgo": DuckDuckGoSearchEngine(),
        "bing": BingSearchEngine(),
    }
    content_fetcher: WebContentFetcher = WebContentFetcher()
    cache: SearchCache = SearchCache(
        ttl_seconds=(
            getattr(config.search_config, "cache_ttl", 300)
            if config.search_config
            else 300
        ),
        max_entries=(
            getattr(config.search_config, "cache_max_entries", 100)
            if config.search_config
            else 100
        ),
    )

    async def execute(  # type: ignore[override]
        self,
        query: str,
        num_results: int = 5,
        lang: Optional[str] = None,
        country: Optional[str] = None,
        fetch_content: bool = False,
    ) -> SearchResponse:
        """
        Execute a Web search and return detailed search results.

        Args:
            query: The search query to submit to the search engine
            num_results: The number of search results to return (default: 5)
            lang: Language code for search results (default from config)
            country: Country code for search results (default from config)
            fetch_content: Whether to fetch content from result pages (default: False)

        Returns:
            A structured response containing search results and metadata
        """
        # Get settings from config
        retry_delay = (
            getattr(config.search_config, "retry_delay", 60)
            if config.search_config
            else 60
        )
        max_retries = (
            getattr(config.search_config, "max_retries", 3)
            if config.search_config
            else 3
        )

        # Use config values for lang and country if not specified
        if lang is None:
            lang = (
                getattr(config.search_config, "lang", "en")
                if config.search_config
                else "en"
            )

        if country is None:
            country = (
                getattr(config.search_config, "country", "us")
                if config.search_config
                else "us"
            )

        # Check cache first
        cached_results = self.cache.get(query, num_results, lang, country)
        if cached_results is not None:
            logger.info(
                f"🔍 Returning {len(cached_results)} cached results for '{query[:60]}'"
            )
            # Still fetch content if requested
            if fetch_content:
                cached_results = await self._fetch_content_for_results(cached_results)
            return SearchResponse(
                status="success",
                query=query,
                results=cached_results,
                metadata=SearchMetadata(
                    total_results=len(cached_results),
                    language=lang,
                    country=country,
                ),
            )

        search_params = {"lang": lang, "country": country}

        # Try searching with retries when all engines fail
        start_time = time.monotonic()
        for retry_count in range(max_retries + 1):
            results = await self._try_all_engines(query, num_results, search_params)

            if results:
                # Cache the results for future queries
                self.cache.set(query, num_results, lang, country, results)

                # Fetch content if requested
                if fetch_content:
                    results = await self._fetch_content_for_results(results)

                duration = (time.monotonic() - start_time) * 1000

                # Record metrics for observability
                metrics.record(
                    "web_search",
                    duration_ms=duration,
                    success=True,
                    metadata={
                        "query": query[:60],
                        "engine": search_params.get("engine", "auto"),
                        "cached": False,
                        "results_count": len(results),
                    },
                )

                return SearchResponse(
                    status="success",
                    query=query,
                    results=results,
                    metadata=SearchMetadata(
                        total_results=len(results),
                        language=lang,
                        country=country,
                    ),
                )

            if retry_count < max_retries:
                # All engines failed, wait and retry
                logger.warning(
                    f"All search engines failed. Waiting {retry_delay} seconds before retry {retry_count + 1}/{max_retries}..."
                )
                await asyncio.sleep(retry_delay)
            else:
                logger.error(
                    f"All search engines failed after {max_retries} retries. Giving up."
                )

        duration = (time.monotonic() - start_time) * 1000
        metrics.record(
            "web_search",
            duration_ms=duration,
            success=False,
            metadata={"query": query[:60], "reason": "all_engines_failed"},
        )

        # Return an error response
        return SearchResponse(
            query=query,
            error="All search engines failed to return results after multiple retries.",
            results=[],
        )

    async def _try_all_engines(
        self, query: str, num_results: int, search_params: Dict[str, Any]
    ) -> List[SearchResult]:
        """Try all search engines in the configured order."""
        engine_order = self._get_engine_order()
        failed_engines = []

        for engine_name in engine_order:
            engine = self._search_engine[engine_name]
            logger.info(f"🔎 Attempting search with {engine_name.capitalize()}...")

            start = time.monotonic()
            search_items = await self._perform_search_with_engine(
                engine, query, num_results, search_params
            )
            duration = (time.monotonic() - start) * 1000

            if not search_items:
                failed_engines.append(engine_name)
                metrics.record(
                    "search_engine",
                    duration_ms=duration,
                    success=False,
                    metadata={"engine": engine_name, "query": query[:60]},
                )
                continue

            if failed_engines:
                logger.info(
                    f"Search successful with {engine_name.capitalize()} after trying: {', '.join(failed_engines)}"
                )

            metrics.record(
                "search_engine",
                duration_ms=duration,
                success=True,
                metadata={"engine": engine_name, "query": query[:60]},
            )

            # Transform search items into structured results
            return [
                SearchResult(
                    position=i + 1,
                    url=item.url,
                    title=item.title
                    or f"Result {i+1}",  # Ensure we always have a title
                    description=item.description or "",
                    source=engine_name,
                )
                for i, item in enumerate(search_items)
            ]

        if failed_engines:
            logger.error(f"All search engines failed: {', '.join(failed_engines)}")
        return []

    async def _fetch_content_for_results(
        self, results: List[SearchResult]
    ) -> List[SearchResult]:
        """Fetch and add web content to search results."""
        if not results:
            return []

        # Create tasks for each result
        tasks = [self._fetch_single_result_content(result) for result in results]

        # Type annotation to help type checker
        fetched_results = await asyncio.gather(*tasks)

        # Explicit validation of return type
        return [
            (
                result
                if isinstance(result, SearchResult)
                else SearchResult(**result.dict())
            )
            for result in fetched_results
        ]

    async def _fetch_single_result_content(self, result: SearchResult) -> SearchResult:
        """Fetch content for a single search result."""
        if result.url:
            content = await self.content_fetcher.fetch_content(result.url)
            if content:
                result.raw_content = content
        return result

    def _get_engine_order(self) -> List[str]:
        """Determines the order in which to try search engines."""
        preferred = (
            getattr(config.search_config, "engine", "google").lower()
            if config.search_config
            else "google"
        )
        fallbacks = (
            [engine.lower() for engine in config.search_config.fallback_engines]
            if config.search_config
            and hasattr(config.search_config, "fallback_engines")
            else []
        )

        # Start with preferred engine, then fallbacks, then remaining engines
        engine_order = [preferred] if preferred in self._search_engine else []
        engine_order.extend(
            [
                fb
                for fb in fallbacks
                if fb in self._search_engine and fb not in engine_order
            ]
        )
        engine_order.extend([e for e in self._search_engine if e not in engine_order])

        return engine_order

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10)
    )
    async def _perform_search_with_engine(
        self,
        engine: WebSearchEngine,
        query: str,
        num_results: int,
        search_params: Dict[str, Any],
    ) -> List[SearchItem]:
        """Execute search with the given engine and parameters."""
        return await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: list(
                engine.perform_search(
                    query,
                    num_results=num_results,
                    lang=search_params.get("lang"),
                    country=search_params.get("country"),
                )
            ),
        )


if __name__ == "__main__":
    web_search = WebSearch()
    search_response = asyncio.run(
        web_search.execute(
            query="Python programming", fetch_content=True, num_results=1
        )
    )
    print(search_response)
