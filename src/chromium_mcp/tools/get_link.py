"""Get link tool implementation."""

import json
import sys
from playwright.async_api import (
    async_playwright,
    TimeoutError as PlaywrightTimeoutError,
)
from ..config import Config
from .fetch_page import validate_url


async def get_link_async(
    url: str,
    selector: str,
    click: bool = False,
    timeout: int = 30,
) -> str:
    """
    Get link href and text from a web page, optionally clicking and following navigation.

    Args:
        url: The URL of the page containing the link
        selector: CSS selector for the anchor element
        click: If True, click the link and follow navigation (default: False)
        timeout: Timeout in seconds (default: 30)

    Returns:
        JSON string with link data:
        - Without click: {"href": "...", "text": "..."}
        - With click: {"href": "...", "text": "...", "final_url": "..."}

    Raises:
        ValueError: If url is invalid, uses unsupported protocol, or element not found
        TimeoutError: If page load or click times out
    """
    # Debug logging
    if Config.is_debug():
        print(f"DEBUG: URL = {url}", file=sys.stderr)
        print(f"DEBUG: selector = {selector}", file=sys.stderr)
        print(f"DEBUG: click = {click}", file=sys.stderr)
        print(f"DEBUG: launching browser...", file=sys.stderr)

    # Validate URL first (before launching browser)
    validate_url(url)

    timeout_ms = timeout * 1000  # Convert to milliseconds for Playwright

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                executable_path=Config.get_chromium_path(),
                headless=Config.is_headless(),
            )
            try:
                page = await browser.new_page()
                page.set_default_timeout(timeout_ms)

                # Navigate to URL
                await page.goto(url, wait_until="domcontentloaded")

                # Get the locator for the anchor element
                locator = page.locator(selector)

                # Get href attribute
                href = await locator.get_attribute("href")

                # Get text content
                text = await locator.text_content()

                # Check if element was found
                if href is None and text is None:
                    raise ValueError(f"Element with selector '{selector}' not found")

                # Strip text if present
                if text:
                    text = text.strip()

                result = {"href": href, "text": text}

                # If click is True, click and follow navigation
                if click:
                    # Use expect_navigation to wait for navigation after click
                    async with page.expect_navigation():
                        await locator.click()

                    # Get final URL after navigation
                    final_url = page.url
                    result["final_url"] = final_url

                return json.dumps(result)

            finally:
                # Always close browser
                await browser.close()

    except PlaywrightTimeoutError as e:
        raise TimeoutError(f"Page load or navigation timed out: {e}") from e
