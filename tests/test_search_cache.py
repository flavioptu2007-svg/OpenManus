"""Tests for Sprint 6 — Search cache and observability metrics."""

import time

import pytest

from app.tool.search.base import SearchItem
from app.tool.web_search import SearchCache, SearchResult
from app.utils.metrics import MetricsCollector


# ─── SearchCache Tests ───────────────────────────────────────────────────────


@pytest.fixture
def sample_results():
    """Create a sample list of search results."""
    return [
        SearchResult(
            position=1,
            url="https://example.com/1",
            title="Result 1",
            description="First result",
            source="google",
        ),
        SearchResult(
            position=2,
            url="https://example.com/2",
            title="Result 2",
            description="Second result",
            source="google",
        ),
    ]


def test_cache_set_and_get(sample_results):
    """Test basic set and get operations."""
    cache = SearchCache(ttl_seconds=300, max_entries=100)
    assert cache.get("test query", 5, "en", "us") is None  # Miss

    cache.set("test query", 5, "en", "us", sample_results)
    cached = cache.get("test query", 5, "en", "us")
    assert cached is not None
    assert len(cached) == 2
    assert cached[0].title == "Result 1"
    assert cached[1].url == "https://example.com/2"


def test_cache_case_insensitivity(sample_results):
    """Test that cache key is case-insensitive."""
    cache = SearchCache()
    cache.set("Hello World", 3, "en", "us", sample_results)

    # Different case should still hit
    cached = cache.get("hello world", 3, "en", "us")
    assert cached is not None

    # Different query should miss
    cached = cache.get("other query", 3, "en", "us")
    assert cached is None


def test_cache_ttl_expiry(sample_results):
    """Test that cache entries expire after TTL."""
    cache = SearchCache(ttl_seconds=0.1, max_entries=100)  # 100ms TTL
    cache.set("test", 5, "en", "us", sample_results)

    # Should be available immediately
    assert cache.get("test", 5, "en", "us") is not None

    # Wait for expiry
    time.sleep(0.15)
    assert cache.get("test", 5, "en", "us") is None  # Expired


def test_cache_max_entries():
    """Test that cache respects max_entries limit."""
    cache = SearchCache(ttl_seconds=300, max_entries=3)

    # Add 4 entries (should evict oldest)
    for i in range(4):
        results = [
            SearchResult(
                position=1,
                url=f"https://example.com/{i}",
                title=f"Result {i}",
                description="",
                source="test",
            )
        ]
        cache.set(f"query_{i}", 1, "en", "us", results)

    # First entry should be evicted
    assert cache.get("query_0", 1, "en", "us") is None
    # Later entries should exist
    assert cache.get("query_3", 1, "en", "us") is not None


def test_cache_invalidate_all(sample_results):
    """Test invalidating entire cache."""
    cache = SearchCache()
    cache.set("query1", 5, "en", "us", sample_results)
    cache.set("query2", 5, "en", "us", sample_results)

    assert cache.get("query1", 5, "en", "us") is not None
    cache.invalidate()
    assert cache.get("query1", 5, "en", "us") is None
    assert cache.get("query2", 5, "en", "us") is None


def test_cache_stats(sample_results):
    """Test cache statistics reporting."""
    cache = SearchCache()

    # No data yet
    stats = cache.stats
    assert stats["hits"] == 0
    assert stats["misses"] == 0
    assert stats["size"] == 0

    # One miss
    cache.get("test", 5, "en", "us")

    # One set + hit
    cache.set("test", 5, "en", "us", sample_results)
    cache.get("test", 5, "en", "us")

    stats = cache.stats
    assert stats["hits"] == 1
    assert stats["misses"] == 1
    assert stats["size"] == 1
    assert "hit_rate" in stats


# ─── MetricsCollector Tests ──────────────────────────────────────────────────


@pytest.fixture
def collector():
    """Creates a fresh MetricsCollector instance."""
    return MetricsCollector(enabled=True)


def test_metrics_record(collector):
    """Test recording a single metric."""
    collector.record("test_op", duration_ms=150.0, success=True)
    assert collector.total_operations == 1
    assert collector.success_rate == 1.0


def test_metrics_record_with_metadata(collector):
    """Test recording with metadata."""
    collector.record(
        "web_search",
        duration_ms=200.0,
        success=True,
        metadata={"engine": "google", "cached": False},
    )

    report = collector.report()
    assert report["operations"]["web_search"]["count"] == 1
    assert report["operations"]["web_search"]["avg_duration_ms"] == 200.0


def test_metrics_success_rate(collector):
    """Test success rate calculation."""
    collector.record("op", 100.0, success=True)
    collector.record("op", 200.0, success=False)
    collector.record("op", 150.0, success=True)

    assert collector.success_rate == 2 / 3
    report = collector.report()
    assert report["summary"]["total_success"] == 2
    assert report["summary"]["total_failures"] == 1


def test_metrics_multiple_operations(collector):
    """Test tracking multiple operation types."""
    collector.record("search", 100.0, True)
    collector.record("search", 200.0, True)
    collector.record("llm", 5000.0, True)

    report = collector.report()
    assert report["operations"]["search"]["count"] == 2
    assert report["operations"]["llm"]["count"] == 1
    assert report["operations"]["search"]["avg_duration_ms"] == 150.0
    assert report["operations"]["llm"]["avg_duration_ms"] == 5000.0


def test_metrics_reset(collector):
    """Test resetting all metrics."""
    collector.record("op", 100.0, True)
    assert collector.total_operations == 1

    collector.reset()
    assert collector.total_operations == 0


def test_metrics_disabled():
    """Test that disabled collector does not record."""
    collector = MetricsCollector(enabled=False)
    collector.record("op", 100.0, True)
    assert collector.total_operations == 0


def test_metrics_empty_report(collector):
    """Test report with no data."""
    report = collector.report()
    assert report["status"] == "no_data"


# ─── SearchResult Tests ──────────────────────────────────────────────────────


def test_search_result_string():
    """Test SearchResult string representation."""
    result = SearchResult(
        position=1,
        url="https://example.com",
        title="Test Title",
        description="A test description",
        source="google",
    )
    assert "Test Title" in str(result)
    assert "example.com" in str(result)
