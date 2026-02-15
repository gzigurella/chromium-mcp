"""Fetch page tool implementation."""

import html2text
from urllib.parse import urlparse
from playwright.async_api import (
    async_playwright,
    TimeoutError as PlaywrightTimeoutError,
)


def validate_url(url: str) -> None:
    """
    Validate URL scheme and format.

    Args:
        url: URL to validate

    Raises:
        ValueError: If URL is invalid or uses unsupported protocol
    """
    if not url or not url.strip():
        raise ValueError("Invalid URL: empty URL")

    try:
        parsed = urlparse(url)
    except Exception as e:
        raise ValueError(f"Invalid URL: {e}")

    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Unsupported protocol: {parsed.scheme or 'none'}")

    if not parsed.netloc:
        raise ValueError("Invalid URL: missing host")


def html_to_markdown(html: str) -> str:
    """
    Convert HTML content to markdown.

    Args:
        html: HTML content to convert

    Returns:
        Markdown formatted string
    """
    converter = html2text.HTML2Text()
    converter.ignore_links = False
    converter.ignore_images = False
    converter.ignore_emphasis = False
    converter.body_width = 0  # Don't wrap lines
    return converter.handle(html)


async def fetch_page_async(
    url: str, timeout: int = 30, wait_for: str | None = None, format: str = "markdown"
) -> str:
    """
    Fetch a web page using Chromium headless browser.

    Args:
        url: The URL to fetch
        timeout: Timeout in seconds (default: 30)
        wait_for: Optional CSS selector to wait for before extracting content
        format: Output format - "markdown" or "html" (default: "markdown")

    Returns:
        String with the fetched page content (markdown or HTML)

    Raises:
        ValueError: If url is invalid or uses unsupported protocol
        TimeoutError: If page load or wait_for times out
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

                # Wait for selector if specified
                if wait_for:
                    await page.wait_for_selector(wait_for, timeout=timeout_ms)

                # Get page content
                html_content = await page.content()

            finally:
                # Always close browser
                await browser.close()

        # Convert to requested format
        if format == "html":
            return html_content
        else:
            return html_to_markdown(html_content)

    except PlaywrightTimeoutError as e:
        raise TimeoutError(f"Page load or wait_for timed out: {e}") from e
