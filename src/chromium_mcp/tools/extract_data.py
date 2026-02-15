"""Extract data tool implementation."""

import json
from playwright.async_api import (
    async_playwright,
    TimeoutError as PlaywrightTimeoutError,
)
from .fetch_page import validate_url


async def extract_data_async(
    url: str,
    selectors: list[dict],
    timeout: int = 30,
) -> str:
    """
    Extract structured data from a web page using CSS selectors.

    Args:
        url: The URL to extract data from
        selectors: List of selector definitions with format:
            {"name": str, "selector": str, "attribute": str (optional), "multiple": bool (optional)}
        timeout: Timeout in seconds (default: 30)

    Returns:
        JSON string with extracted data

    Raises:
        ValueError: If url is invalid or uses unsupported protocol
        TimeoutError: If page load times out
    """
    # Validate URL first (before launching browser)
    validate_url(url)

    timeout_ms = timeout * 1000  # Convert to milliseconds for Playwright
    result = {}

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            try:
                page = await browser.new_page()
                page.set_default_timeout(timeout_ms)

                # Navigate to URL
                await page.goto(url, wait_until="domcontentloaded")

                # Extract data for each selector
                for sel_def in selectors:
                    name = sel_def.get("name")
                    selector = sel_def.get("selector")
                    attribute = sel_def.get("attribute")
                    multiple = sel_def.get("multiple", False)

                    if not name or not selector:
                        continue

                    locator = page.locator(selector)

                    if multiple:
                        # Extract multiple elements
                        count = await locator.count()
                        values = []

                        for i in range(count):
                            element = locator.nth(i)
                            if attribute:
                                val = await element.get_attribute(attribute)
                            else:
                                val = await element.text_content()
                                if val:
                                    val = val.strip()
                            values.append(val)

                        result[name] = values
                    else:
                        # Extract single element
                        if attribute:
                            result[name] = await locator.get_attribute(attribute)
                        else:
                            val = await locator.text_content()
                            result[name] = val.strip() if val else val

            finally:
                # Always close browser
                await browser.close()

        return json.dumps(result, indent=2)

    except PlaywrightTimeoutError as e:
        raise TimeoutError(f"Page load timed out: {e}") from e
