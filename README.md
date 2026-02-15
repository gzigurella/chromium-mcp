# Chromium MCP
MCP server for web fetching and automation using Chromium headless browser.

## Reason behind this repository
I didn't wanna waste my "limited" tokens on Z.ai coding plan, therefore I made my own MCP to interact with the web, feel free to propose enhancements or new features.

## Features

- **fetch_page**: Fetch web pages and convert to markdown/HTML
- **screenshot**: Take screenshots of web pages or specific elements
- **interact**: Automate browser interactions (click, fill, scroll, wait)
- **extract_data**: Extract structured data using CSS selectors
- **get_link**: Get link information and follow redirects

## Installation

### From Git Repository

```bash
# Clone the repository
git clone https://github.com/gzigurella/chromium-mcp.git
cd chromium-mcp

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .

# Install Chromium browser (required)
playwright install chromium
```

### With uv (recommended)

```bash
# Clone and enter directory
git clone https://github.com/gzigurella/chromium-mcp.git
cd chromium-mcp

# Install with uv
uv pip install -e .

# Install Chromium
playwright install chromium
```

## Integration

### OpenCode

Add to your `~/.config/opencode/opencode.json`:

```json
{
  "mcpServers": {
    "chromium-fetch": {
      "type": "local",
      "command": [
        "/path/to/chromium-mcp/venv/bin/python",
        "-m",
        "chromium_mcp"
      ],
      "enabled": true
    }
  }
}
```

### Claude Desktop

Add to your Claude Desktop config:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "chromium-fetch": {
      "command": "/path/to/chromium-mcp/venv/bin/python",
      "args": ["-m", "chromium_mcp"]
    }
  }
}
```

### Generic MCP Client

For any MCP-compatible client:

```bash
# Start the server directly
/path/to/venv/bin/python -m chromium_mcp
```

The server communicates via stdio using the MCP protocol.

## Tools

### fetch_page

Fetch a web page and return content as markdown or HTML.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| url | string | Yes | - | URL to fetch |
| format | string | No | "markdown" | Output format: "markdown" or "html" |
| timeout | integer | No | 30 | Timeout in seconds |
| wait_for | string | No | null | CSS selector to wait for |

```json
{
  "url": "https://example.com",
  "format": "markdown",
  "timeout": 30,
  "wait_for": ".main-content"
}
```

### screenshot

Take a screenshot of a web page.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| url | string | Yes | - | URL to screenshot |
| format | string | No | "png" | Image format: "png" or "jpeg" |
| quality | integer | No | 80 | JPEG quality (1-100) |
| full_page | boolean | No | false | Capture full page |
| selector | string | No | null | CSS selector for element |
| timeout | integer | No | 30 | Timeout in seconds |

```json
{
  "url": "https://example.com",
  "format": "png",
  "full_page": true
}
```

### interact

Interact with web page elements sequentially.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| url | string | Yes | - | URL to interact with |
| actions | array | Yes | - | List of actions |
| timeout | integer | No | 30 | Timeout in seconds |

**Action Types:**
- `click`: Click element by selector
- `fill`: Fill input field
- `select`: Select dropdown option
- `scroll`: Scroll page
- `wait`: Wait for element

```json
{
  "url": "https://example.com/search",
  "actions": [
    {"type": "fill", "selector": "input[name='q']", "value": "test search"},
    {"type": "click", "selector": "button[type='submit']"},
    {"type": "wait", "selector": ".results", "milliseconds": 2000}
  ]
}
```

### extract_data

Extract structured data using CSS selectors.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| url | string | Yes | - | URL to extract from |
| selectors | array | Yes | - | List of extraction rules |
| timeout | integer | No | 30 | Timeout in seconds |

```json
{
  "url": "https://example.com/products",
  "selectors": [
    {"name": "titles", "selector": "h2.product-title", "multiple": true},
    {"name": "prices", "selector": ".price", "multiple": true},
    {"name": "links", "selector": "a.product-link", "attribute": "href", "multiple": true}
  ]
}
```

### get_link

Get link href and text, optionally following navigation.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| url | string | Yes | - | URL of page containing link |
| selector | string | Yes | - | CSS selector for anchor |
| click | boolean | No | false | Follow the link |
| timeout | integer | No | 30 | Timeout in seconds |

```json
{
  "url": "https://example.com",
  "selector": "a.download",
  "click": true
}
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| CHROMIUM_PATH | auto | Path to Chromium executable |
| HEADLESS | true | Run browser in headless mode |
| TIMEOUT | 30 | Default operation timeout |
| DEBUG | false | Enable debug logging |

```bash
# Example
export TIMEOUT=60
export HEADLESS=false
python -m chromium_mcp
```

## Development

### Running Tests

```bash
source venv/bin/activate
pytest

# With coverage
pytest --cov=src --cov-report=html
```

### Project Structure

```
chromium-mcp/
├── src/chromium_mcp/
│   ├── __init__.py
│   ├── __main__.py
│   ├── server.py
│   └── tools/
│       ├── __init__.py
│       ├── fetch_page.py
│       ├── screenshot.py
│       ├── interact.py
│       ├── extract_data.py
│       └── get_link.py
├── tests/
├── pyproject.toml
└── README.md
```

## Troubleshooting

### Browser Not Found

```bash
playwright install chromium
```

### Permission Issues (Linux)

```bash
sudo sysctl -w kernel.shmmax=268435456
```

### Timeout Errors

```bash
export TIMEOUT=60
```

## Security

- `file://` URLs are blocked
- Credentials are never logged
- Browser processes are always cleaned up
- All operations have configurable timeouts

## License

MIT
