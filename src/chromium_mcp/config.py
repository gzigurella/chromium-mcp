"""
Configuration module for Chromium MCP.

Environment Variables:
- CHROMIUM_PATH: Path to Chromium executable (optional, playwright auto-detects if not set)
- HEADLESS: Run browser in headless mode (default: true)
- TIMEOUT: Default timeout in seconds for operations (default: 30)
- DEBUG: Enable debug logging (default: false)

Boolean values can be specified case-insensitively as "true", "1", "yes", or "on" for True.
"""

import os


class Config:
    """Configuration class for environment variable handling."""

    @classmethod
    def get_chromium_path(cls) -> str | None:
        """
        Get Chromium executable path from environment variable.

        Returns:
            str | None: CHROMIUM_PATH value or None if not set (playwright will auto-detect)
        """
        return os.environ.get("CHROMIUM_PATH")

    @classmethod
    def is_headless(cls) -> bool:
        """
        Get headless mode setting from environment variable.

        Returns:
            bool: True if HEADLESS is set to true/1/yes/on, False otherwise (default: True)
        """
        value = os.environ.get("HEADLESS", "true").lower()

        if value in ("true", "1", "yes", "on"):
            return True
        return False

    @classmethod
    def get_timeout(cls) -> int:
        """
        Get default timeout in seconds from environment variable.

        Returns:
            int: TIMEOUT value converted to int (default: 30)

        Raises:
            ValueError: If TIMEOUT is set but cannot be converted to int
        """
        value = os.environ.get("TIMEOUT", "30")

        try:
            return int(value)
        except ValueError as e:
            raise ValueError(
                f"Invalid TIMEOUT value '{value}': must be an integer"
            ) from e

    @classmethod
    def is_debug(cls) -> bool:
        """
        Get debug mode setting from environment variable.

        Returns:
            bool: True if DEBUG is set to true/1/yes/on, False otherwise (default: False)
        """
        value = os.environ.get("DEBUG", "false").lower()

        if value in ("true", "1", "yes", "on"):
            return True
        return False
