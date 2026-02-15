"""Screenshot tool implementation."""

import base64
from playwright.async_api import (
    async_playwright,
    TimeoutError as PlaywrightTimeoutError,
)
from .fetch_page import validate_url


async def screenshot_async(
    url: str,
    format: str = "png",
    quality: int = 80,
    full_page: bool = False,
    selector: str | None = None,
    timeout: int = 30,
) -> str:
    """
    Take a screenshot of a web page using Chromium headless browser.

    Args:
        url: The URL to screenshot (must be http or https)
        format: Image format - "png" (default) or "jpeg"
        quality: JPEG quality 1-100 (default: 80, only used for jpeg)
        full_page: Take full page screenshot (default: False)
        selector: Optional CSS selector for element screenshot
        timeout: Timeout in seconds (default: 30)

    Returns:
        Base64-encoded image string

    Raises:
        ValueError: If url is invalid or uses unsupported protocol
        TimeoutError: If page load times out
    """
    # Validate URL first (before launching browser)
    validate_url(url)

    timeout_ms = timeout * 1000  # Convert to milliseconds for Playwright

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            try:
                page = await browser.new_page()
                page.set_default_timeout(timeout_ms)

                # Navigate to URL
                await page.goto(url, wait_until="domcontentloaded")

                # Build screenshot options
                screenshot_options = {
                    "type": format,
                }

                # full_page is only valid for page screenshot, not locator
                if not selector:
                    screenshot_options["full_page"] = full_page

                # Quality is only valid for JPEG
                if format == "jpeg":
                    screenshot_options["quality"] = quality

                # Take screenshot - either full page, element, or viewport
                if selector:
                    # Element screenshot using locator
                    locator = page.locator(selector)
                    screenshot_bytes = await locator.screenshot(**screenshot_options)
                else:
                    # Page screenshot
                    screenshot_bytes = await page.screenshot(**screenshot_options)

            finally:
                # Always close browser
                await browser.close()

        # Convert to base64
        base64_image = base64.b64encode(screenshot_bytes).decode("utf-8")
        return base64_image

    except PlaywrightTimeoutError as e:
        raise TimeoutError(f"Page load timed out: {e}") from e
