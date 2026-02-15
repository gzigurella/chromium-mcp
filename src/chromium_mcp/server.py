"""MCP server for Chromium-based web fetching."""

import asyncio
import sys
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from .config import Config


# Create server instance
server = Server("chromium-mcp")


@server.list_tools()
async def list_tools():
    """List available tools."""
    return [
        Tool(
            name="fetch_page",
            description="Fetch a web page using Chromium headless browser and return content as markdown or HTML. "
            "Useful for reading web pages, extracting content from dynamic sites that require JavaScript rendering.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to fetch (must be http or https)",
                    },
                    "timeout": {
                        "type": "integer",
                        "default": 30,
                        "description": "Timeout in seconds (default: 30)",
                    },
                    "wait_for": {
                        "type": "string",
                        "description": "Optional CSS selector to wait for before extracting content. "
                        "Useful for pages that load content dynamically.",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["markdown", "html"],
                        "default": "markdown",
                        "description": "Output format - 'markdown' (default) or 'html'",
                    },
                },
                "required": ["url"],
            },
        ),
        Tool(
            name="screenshot",
            description="Take a screenshot of a web page using Chromium headless browser. "
            "Returns base64-encoded image. Supports PNG and JPEG formats, full page screenshots, "
            "and element screenshots via CSS selector.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to screenshot (must be http or https)",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["png", "jpeg"],
                        "default": "png",
                        "description": "Image format - 'png' (default) or 'jpeg'",
                    },
                    "quality": {
                        "type": "integer",
                        "default": 80,
                        "minimum": 1,
                        "maximum": 100,
                        "description": "JPEG quality 1-100 (default: 80, only for jpeg)",
                    },
                    "full_page": {
                        "type": "boolean",
                        "default": False,
                        "description": "Take full page screenshot (default: False)",
                    },
                    "selector": {
                        "type": "string",
                        "description": "Optional CSS selector for element screenshot",
                    },
                    "timeout": {
                        "type": "integer",
                        "default": 30,
                        "description": "Timeout in seconds (default: 30)",
                    },
                },
                "required": ["url"],
            },
        ),
        Tool(
            name="interact",
            description="Interact with web page elements using Chromium headless browser. "
            "Execute actions like click, fill, select, scroll, and wait in sequence. "
            "Returns the final page content as markdown after all actions are executed.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to interact with (must be http or https)",
                    },
                    "actions": {
                        "type": "array",
                        "description": "List of actions to execute in sequence",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "enum": [
                                        "click",
                                        "fill",
                                        "select",
                                        "scroll",
                                        "wait",
                                    ],
                                    "description": "Type of action to perform",
                                },
                                "selector": {
                                    "type": "string",
                                    "description": "CSS selector (required for click, fill, select)",
                                },
                                "value": {
                                    "type": "string",
                                    "description": "Value to set (required for fill, select)",
                                },
                                "direction": {
                                    "type": "string",
                                    "enum": ["up", "down"],
                                    "description": "Scroll direction (for scroll, default: down)",
                                },
                                "amount": {
                                    "type": "integer",
                                    "description": "Pixels to scroll (for scroll, default: 500)",
                                },
                                "milliseconds": {
                                    "type": "integer",
                                    "description": "Wait time in ms (for wait, default: 1000)",
                                },
                            },
                            "required": ["type"],
                        },
                    },
                    "timeout": {
                        "type": "integer",
                        "default": 30,
                        "description": "Timeout in seconds (default: 30)",
                    },
                },
                "required": ["url", "actions"],
            },
        ),
        Tool(
            name="extract_data",
            description="Extract structured data from a web page using CSS selectors. "
            "Returns JSON with extracted text content or attribute values. "
            "Supports single element, multiple elements, and attribute extraction.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to extract data from (must be http or https)",
                    },
                    "selectors": {
                        "type": "array",
                        "description": "List of CSS selectors with extraction rules",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Name for the extracted data field",
                                },
                                "selector": {
                                    "type": "string",
                                    "description": "CSS selector to match elements",
                                },
                                "attribute": {
                                    "type": "string",
                                    "description": "Attribute to extract (optional, default: text content)",
                                },
                                "multiple": {
                                    "type": "boolean",
                                    "description": "Extract all matching elements as array (optional, default: false)",
                                },
                            },
                            "required": ["name", "selector"],
                        },
                    },
                    "timeout": {
                        "type": "integer",
                        "default": 30,
                        "description": "Timeout in seconds (default: 30)",
                    },
                },
                "required": ["url", "selectors"],
            },
        ),
        Tool(
            name="get_link",
            description="Get link href and text from a web page. "
            "By default extracts href without clicking. When click=true, follows the link and returns the final URL. "
            "Useful for extracting download links, checking redirect destinations, or getting link text.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL of the page containing the link (must be http or https)",
                    },
                    "selector": {
                        "type": "string",
                        "description": "CSS selector for the anchor element",
                    },
                    "click": {
                        "type": "boolean",
                        "default": False,
                        "description": "Click the link and follow navigation (default: False)",
                    },
                    "timeout": {
                        "type": "integer",
                        "default": 30,
                        "description": "Timeout in seconds (default: 30)",
                    },
                },
                "required": ["url", "selector"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """Handle tool calls."""
    if Config.is_debug():
        print(
            f"DEBUG: Tool called: {name}, args: {list(arguments.keys())}",
            file=sys.stderr,
        )
    if name == "fetch_page":
        from .tools.fetch_page import fetch_page_async

        url = arguments.get("url")
        timeout = arguments.get("timeout", 30)
        wait_for = arguments.get("wait_for")
        format = arguments.get("format", "markdown")

        try:
            result = await fetch_page_async(
                url=url, timeout=timeout, wait_for=wait_for, format=format
            )
            return [TextContent(type="text", text=result)]
        except ValueError as e:
            return [TextContent(type="text", text=f"Error: {e}")]
        except TimeoutError as e:
            return [TextContent(type="text", text=f"Error: {e}")]

    if name == "screenshot":
        from .tools.screenshot import screenshot_async

        url = arguments.get("url")
        format = arguments.get("format", "png")
        quality = arguments.get("quality", 80)
        full_page = arguments.get("full_page", False)
        selector = arguments.get("selector")
        timeout = arguments.get("timeout", 30)

        try:
            result = await screenshot_async(
                url=url,
                format=format,
                quality=quality,
                full_page=full_page,
                selector=selector,
                timeout=timeout,
            )
            return [TextContent(type="text", text=result)]
        except ValueError as e:
            return [TextContent(type="text", text=f"Error: {e}")]
        except TimeoutError as e:
            return [TextContent(type="text", text=f"Error: {e}")]

    if name == "interact":
        from .tools.interact import interact_async

        url = arguments.get("url")
        actions = arguments.get("actions", [])
        timeout = arguments.get("timeout", 30)

        try:
            result = await interact_async(
                url=url,
                actions=actions,
                timeout=timeout,
            )
            return [TextContent(type="text", text=result)]
        except ValueError as e:
            return [TextContent(type="text", text=f"Error: {e}")]
        except TimeoutError as e:
            return [TextContent(type="text", text=f"Error: {e}")]

    if name == "extract_data":
        from .tools.extract_data import extract_data_async

        url = arguments.get("url")
        selectors = arguments.get("selectors", [])
        timeout = arguments.get("timeout", 30)

        try:
            result = await extract_data_async(
                url=url,
                selectors=selectors,
                timeout=timeout,
            )
            return [TextContent(type="text", text=result)]
        except ValueError as e:
            return [TextContent(type="text", text=f"Error: {e}")]
        except TimeoutError as e:
            return [TextContent(type="text", text=f"Error: {e}")]

    if name == "get_link":
        from .tools.get_link import get_link_async

        url = arguments.get("url")
        selector = arguments.get("selector")
        click = arguments.get("click", False)
        timeout = arguments.get("timeout", 30)

        try:
            result = await get_link_async(
                url=url,
                selector=selector,
                click=click,
                timeout=timeout,
            )
            return [TextContent(type="text", text=result)]
        except ValueError as e:
            return [TextContent(type="text", text=f"Error: {e}")]
        except TimeoutError as e:
            return [TextContent(type="text", text=f"Error: {e}")]

    raise NotImplementedError(f"Tool {name} not implemented")


async def main():
    """Main entry point for STDIO transport."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )


def run():
    """Run the MCP server from command line entry point."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
