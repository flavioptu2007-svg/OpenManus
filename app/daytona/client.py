"""Shared Daytona client initialization — single source of truth.

Both sandbox.py and tool_base.py previously duplicated this lazy-init logic.
Import `daytona` and `_ensure_daytona()` from here instead.
"""

from typing import Optional

from daytona import Daytona, DaytonaConfig

from app.config import config
from app.utils.logger import logger


daytona_settings = config.daytona
daytona: Optional[Daytona] = None

if daytona_settings.daytona_api_key:
    try:
        daytona_config = DaytonaConfig(
            api_key=daytona_settings.daytona_api_key,
            server_url=daytona_settings.daytona_server_url,
            target=daytona_settings.daytona_target,
        )
        daytona = Daytona(daytona_config)
        logger.info("Daytona client initialized")

        if daytona_config.server_url:
            logger.info(f"Daytona server URL set to: {daytona_config.server_url}")
        if daytona_config.target:
            logger.info(f"Daytona target set to: {daytona_config.target}")
    except Exception as e:
        logger.warning(f"Failed to initialize Daytona client: {e}")
        daytona = None
else:
    logger.warning("No Daytona API key configured — sandbox features disabled")


def _ensure_daytona() -> Daytona:
    """Ensure Daytona client is available, raise clear error if not."""
    if daytona is None:
        raise RuntimeError(
            "Daytona is not configured. Set a DAYTONA_API_KEY in config.toml "
            "or environment variables to enable sandbox features."
        )
    return daytona
