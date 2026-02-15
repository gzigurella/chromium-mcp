"""Interactive tool implementation for web page automation."""

from playwright.async_api import (
    async_playwright,
    TimeoutError as PlaywrightTimeoutError,
)
from .fetch_page import validate_url, html_to_markdown
from ..config import Config
import sys


# Valid action types
VALID_ACTION_TYPES = frozenset(["click", "fill", "select", "scroll", "wait"])


def validate_actions(actions: list[dict]) -> None:
    """
    Validate action list.

    Args:
        actions: List of action dictionaries

    Raises:
        ValueError: If actions is empty or contains invalid action type
    """
    if not actions:
        raise ValueError("Actions list cannot be empty")

    for action in actions:
        action_type = action.get("type")
        if action_type not in VALID_ACTION_TYPES:
            raise ValueError(f"Invalid action type: {action_type}")


async def execute_action(page, action: dict) -> None:
    """
    Execute a single action on the page.

    Args:
        page: Playwright page object
        action: Action dictionary with type and parameters
    """
    action_type = action["type"]

    if action_type == "click":
        await page.click(action["selector"])

    elif action_type == "fill":
        await page.fill(action["selector"], action["value"])

    elif action_type == "select":
        await page.select_option(action["selector"], action["value"])

    elif action_type == "scroll":
        direction = action.get("direction", "down")
        amount = action.get("amount", 500)
        scroll_amount = amount if direction == "down" else -amount
        await page.evaluate(f"window.scrollBy(0, {scroll_amount})")

    elif action_type == "wait":
        milliseconds = action.get("milliseconds", 1000)
        await page.wait_for_timeout(milliseconds)


async def interact_async(
    url: str,
    actions: list[dict],
    timeout: int = 30,
) -> str:
    """
    Interact with web page elements using Chromium headless browser.

    Args:
        url: The URL to interact with (must be http or https)
        actions: List of actions to perform. Each action is a dict with:
            - type: "click", "fill", "select", "scroll", or "wait"
            - selector: CSS selector (for click, fill, select)
            - value: Value to set (for fill, select)
            - direction: "up" or "down" (for scroll, default: "down")
            - amount: Pixels to scroll (for scroll, default: 500)
            - milliseconds: Wait time in ms (for wait, default: 1000)
        timeout: Timeout in seconds (default: 30)

    Returns:
        Final page content as markdown after all actions are executed

    Raises:
        ValueError: If url is invalid, actions empty, or invalid action type
        TimeoutError: If page load or action times out
    """
    # Validate URL first (before launching browser)
    validate_url(url)

    # Validate actions
    validate_actions(actions)

    timeout_ms = timeout * 1000  # Convert to milliseconds for Playwright

    if Config.is_debug():
        print(f"DEBUG: Starting interact_async", file=sys.stderr)
        print(f"DEBUG: URL: {url}", file=sys.stderr)
        print(f"DEBUG: Number of actions: {len(actions)}", file=sys.stderr)

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                executable_path=Config.get_chromium_path(),
                headless=Config.is_headless(),
            )
            if Config.is_debug():
                print(f"DEBUG: Browser launched", file=sys.stderr)
            try:
                page = await browser.new_page()
                page.set_default_timeout(timeout_ms)

                # Navigate to URL
                await page.goto(url, wait_until="domcontentloaded")

                # Execute all actions in sequence
                for action in actions:
                    await execute_action(page, action)

                # Get final page content
                html_content = await page.content()

            finally:
                # Always close browser
                await browser.close()

        # Return content as markdown
        return html_to_markdown(html_content)

    except PlaywrightTimeoutError as e:
        raise TimeoutError(f"Page load or action timed out: {e}") from e
