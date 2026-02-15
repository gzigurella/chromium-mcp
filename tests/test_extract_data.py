"""Test extract_data tool with TDD RED phase - tests expected to FAIL."""

import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock


def create_mock_locator():
    """Helper to create a properly mocked Playwright locator."""
    locator = MagicMock()
    locator.text_content = AsyncMock()
    locator.get_attribute = AsyncMock()
    locator.count = AsyncMock()
    locator.nth = MagicMock()  # nth() is sync, returns another locator
    return locator


def create_mock_page():
    """Helper to create a properly mocked Playwright page."""
    page = MagicMock()
    page.goto = AsyncMock()
    page.content = AsyncMock()
    page.set_default_timeout = MagicMock()  # Sync method
    page.locator = MagicMock()  # Sync method returning locator
    return page


class TestExtractDataURLValidation:
    """Test URL validation for extract_data tool."""

    @pytest.mark.asyncio
    async def test_file_url_raises_unsupported_protocol_error(self):
        """Test that file:// URLs raise ValueError with 'Unsupported protocol' message."""
        from chromium_mcp.tools.extract_data import extract_data_async

        selectors = [{"name": "title", "selector": "h1"}]

        with pytest.raises(ValueError) as exc_info:
            await extract_data_async(url="file:///etc/passwd", selectors=selectors)

        assert "Unsupported protocol" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invalid_url_raises_value_error(self):
        """Test that malformed URLs raise ValueError."""
        from chromium_mcp.tools.extract_data import extract_data_async

        selectors = [{"name": "title", "selector": "h1"}]

        with pytest.raises(ValueError):
            await extract_data_async(url="not-a-valid-url", selectors=selectors)

    @pytest.mark.asyncio
    async def test_empty_url_raises_value_error(self):
        """Test that empty URL raises ValueError."""
        from chromium_mcp.tools.extract_data import extract_data_async

        selectors = [{"name": "title", "selector": "h1"}]

        with pytest.raises(ValueError):
            await extract_data_async(url="", selectors=selectors)


class TestExtractDataTextExtraction:
    """Test text extraction from selectors."""

    @pytest.mark.asyncio
    async def test_extract_single_text_returns_text(self):
        """Test extracting text from a single selector returns text content."""
        from chromium_mcp.tools.extract_data import extract_data_async

        selectors = [{"name": "title", "selector": "h1"}]

        with patch(
            "chromium_mcp.tools.extract_data.async_playwright"
        ) as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = create_mock_page()
            mock_locator = create_mock_locator()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.locator.return_value = mock_locator
            mock_locator.text_content.return_value = "Page Title"

            result = await extract_data_async(
                url="https://example.com", selectors=selectors
            )

            # Result should be JSON string
            parsed = json.loads(result)
            assert parsed["title"] == "Page Title"

    @pytest.mark.asyncio
    async def test_extract_empty_text_returns_empty_string(self):
        """Test that element with no text returns empty string."""
        from chromium_mcp.tools.extract_data import extract_data_async

        selectors = [{"name": "empty", "selector": ".empty-element"}]

        with patch(
            "chromium_mcp.tools.extract_data.async_playwright"
        ) as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = create_mock_page()
            mock_locator = create_mock_locator()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.locator.return_value = mock_locator
            mock_locator.text_content.return_value = ""

            result = await extract_data_async(
                url="https://example.com", selectors=selectors
            )

            parsed = json.loads(result)
            assert parsed["empty"] == ""


class TestExtractDataAttributeExtraction:
    """Test attribute extraction from elements."""

    @pytest.mark.asyncio
    async def test_extract_attribute_returns_attribute_value(self):
        """Test extracting an attribute from an element returns attribute value."""
        from chromium_mcp.tools.extract_data import extract_data_async

        selectors = [{"name": "link", "selector": "a.main", "attribute": "href"}]

        with patch(
            "chromium_mcp.tools.extract_data.async_playwright"
        ) as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = create_mock_page()
            mock_locator = create_mock_locator()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.locator.return_value = mock_locator
            mock_locator.get_attribute.return_value = "https://example.com/page"

            result = await extract_data_async(
                url="https://example.com", selectors=selectors
            )

            parsed = json.loads(result)
            assert parsed["link"] == "https://example.com/page"

    @pytest.mark.asyncio
    async def test_extract_missing_attribute_returns_null(self):
        """Test that missing attribute returns null."""
        from chromium_mcp.tools.extract_data import extract_data_async

        selectors = [{"name": "missing", "selector": "div", "attribute": "data-value"}]

        with patch(
            "chromium_mcp.tools.extract_data.async_playwright"
        ) as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = create_mock_page()
            mock_locator = create_mock_locator()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.locator.return_value = mock_locator
            mock_locator.get_attribute.return_value = None

            result = await extract_data_async(
                url="https://example.com", selectors=selectors
            )

            parsed = json.loads(result)
            assert parsed["missing"] is None


class TestExtractDataMultipleElements:
    """Test multiple element extraction."""

    @pytest.mark.asyncio
    async def test_extract_multiple_elements_returns_array(self):
        """Test extracting multiple elements returns array of values."""
        from chromium_mcp.tools.extract_data import extract_data_async

        selectors = [{"name": "items", "selector": "li", "multiple": True}]

        with patch(
            "chromium_mcp.tools.extract_data.async_playwright"
        ) as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = create_mock_page()
            mock_locator = create_mock_locator()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.locator.return_value = mock_locator
            mock_locator.count.return_value = 3

            # Setup nth locator mocks
            def nth_side_effect(i):
                nth_loc = create_mock_locator()
                nth_loc.text_content.return_value = f"Item {i + 1}"
                return nth_loc

            mock_locator.nth.side_effect = nth_side_effect

            result = await extract_data_async(
                url="https://example.com", selectors=selectors
            )

            parsed = json.loads(result)
            assert parsed["items"] == ["Item 1", "Item 2", "Item 3"]

    @pytest.mark.asyncio
    async def test_extract_multiple_with_attribute_returns_array(self):
        """Test extracting multiple elements with attribute returns array of attribute values."""
        from chromium_mcp.tools.extract_data import extract_data_async

        selectors = [
            {"name": "links", "selector": "a", "attribute": "href", "multiple": True}
        ]

        with patch(
            "chromium_mcp.tools.extract_data.async_playwright"
        ) as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = create_mock_page()
            mock_locator = create_mock_locator()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.locator.return_value = mock_locator
            mock_locator.count.return_value = 2

            def nth_side_effect(i):
                nth_loc = create_mock_locator()
                nth_loc.get_attribute.return_value = f"https://example.com/link{i + 1}"
                return nth_loc

            mock_locator.nth.side_effect = nth_side_effect

            result = await extract_data_async(
                url="https://example.com", selectors=selectors
            )

            parsed = json.loads(result)
            assert parsed["links"] == [
                "https://example.com/link1",
                "https://example.com/link2",
            ]

    @pytest.mark.asyncio
    async def test_extract_multiple_no_elements_returns_empty_array(self):
        """Test extracting multiple elements with no matches returns empty array."""
        from chromium_mcp.tools.extract_data import extract_data_async

        selectors = [{"name": "items", "selector": ".nonexistent", "multiple": True}]

        with patch(
            "chromium_mcp.tools.extract_data.async_playwright"
        ) as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = create_mock_page()
            mock_locator = create_mock_locator()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.locator.return_value = mock_locator
            mock_locator.count.return_value = 0

            result = await extract_data_async(
                url="https://example.com", selectors=selectors
            )

            parsed = json.loads(result)
            assert parsed["items"] == []


class TestExtractDataMultipleSelectors:
    """Test extraction with multiple selectors in single call."""

    @pytest.mark.asyncio
    async def test_extract_multiple_selectors_returns_object(self):
        """Test extracting multiple selectors returns object with all values."""
        from chromium_mcp.tools.extract_data import extract_data_async

        selectors = [
            {"name": "title", "selector": "h1"},
            {"name": "description", "selector": ".description"},
            {"name": "link", "selector": "a.main", "attribute": "href"},
        ]

        with patch(
            "chromium_mcp.tools.extract_data.async_playwright"
        ) as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = create_mock_page()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page

            # Setup different locators for different selectors
            def create_locator(selector):
                loc = create_mock_locator()
                if selector == "h1":
                    loc.text_content.return_value = "Page Title"
                elif selector == ".description":
                    loc.text_content.return_value = "A description"
                elif selector == "a.main":
                    loc.get_attribute.return_value = "https://example.com/page"
                return loc

            mock_page.locator.side_effect = create_locator

            result = await extract_data_async(
                url="https://example.com", selectors=selectors
            )

            parsed = json.loads(result)
            assert parsed["title"] == "Page Title"
            assert parsed["description"] == "A description"
            assert parsed["link"] == "https://example.com/page"


class TestExtractDataNotFound:
    """Test handling of elements not found."""

    @pytest.mark.asyncio
    async def test_single_element_not_found_returns_null(self):
        """Test that single element not found returns null."""
        from chromium_mcp.tools.extract_data import extract_data_async

        selectors = [{"name": "missing", "selector": ".nonexistent"}]

        with patch(
            "chromium_mcp.tools.extract_data.async_playwright"
        ) as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = create_mock_page()
            mock_locator = create_mock_locator()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.locator.return_value = mock_locator
            mock_locator.text_content.return_value = None

            result = await extract_data_async(
                url="https://example.com", selectors=selectors
            )

            parsed = json.loads(result)
            assert parsed["missing"] is None


class TestExtractDataTimeout:
    """Test timeout handling."""

    @pytest.mark.asyncio
    async def test_timeout_expired_raises_timeout_error(self):
        """Test that timeout expired raises TimeoutError."""
        from chromium_mcp.tools.extract_data import extract_data_async
        from playwright.async_api import TimeoutError as PlaywrightTimeoutError

        selectors = [{"name": "title", "selector": "h1"}]

        with patch(
            "chromium_mcp.tools.extract_data.async_playwright"
        ) as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = create_mock_page()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page

            # Simulate timeout on goto
            mock_page.goto.side_effect = PlaywrightTimeoutError(
                "Timeout 30000ms exceeded"
            )

            with pytest.raises(TimeoutError):
                await extract_data_async(
                    url="https://example.com", selectors=selectors, timeout=1
                )


class TestExtractDataBrowserCleanup:
    """Test browser cleanup on error."""

    @pytest.mark.asyncio
    async def test_browser_closes_on_error(self):
        """Test that browser is closed even when error occurs."""
        from chromium_mcp.tools.extract_data import extract_data_async

        selectors = [{"name": "title", "selector": "h1"}]

        with patch(
            "chromium_mcp.tools.extract_data.async_playwright"
        ) as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = create_mock_page()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page

            # Simulate error after page is created
            mock_page.goto.side_effect = Exception("Network error")

            with pytest.raises(Exception):
                await extract_data_async(url="https://example.com", selectors=selectors)

            # Verify browser was closed
            mock_browser.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_browser_closes_on_success(self):
        """Test that browser is closed after successful extraction."""
        from chromium_mcp.tools.extract_data import extract_data_async

        selectors = [{"name": "title", "selector": "h1"}]

        with patch(
            "chromium_mcp.tools.extract_data.async_playwright"
        ) as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = create_mock_page()
            mock_locator = create_mock_locator()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.locator.return_value = mock_locator
            mock_locator.text_content.return_value = "Title"

            await extract_data_async(url="https://example.com", selectors=selectors)

            # Verify browser was closed
            mock_browser.close.assert_called_once()


class TestExtractDataOutputFormat:
    """Test output format is valid JSON."""

    @pytest.mark.asyncio
    async def test_output_is_valid_json_string(self):
        """Test that output is a valid JSON string."""
        from chromium_mcp.tools.extract_data import extract_data_async

        selectors = [{"name": "title", "selector": "h1"}]

        with patch(
            "chromium_mcp.tools.extract_data.async_playwright"
        ) as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = create_mock_page()
            mock_locator = create_mock_locator()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.locator.return_value = mock_locator
            mock_locator.text_content.return_value = "Test"

            result = await extract_data_async(
                url="https://example.com", selectors=selectors
            )

            # Should be string
            assert isinstance(result, str)
            # Should be valid JSON
            parsed = json.loads(result)
            assert isinstance(parsed, dict)

    @pytest.mark.asyncio
    async def test_empty_selectors_returns_empty_object(self):
        """Test that empty selectors array returns empty JSON object."""
        from chromium_mcp.tools.extract_data import extract_data_async

        selectors = []

        with patch(
            "chromium_mcp.tools.extract_data.async_playwright"
        ) as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = create_mock_page()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page

            result = await extract_data_async(
                url="https://example.com", selectors=selectors
            )

            parsed = json.loads(result)
            assert parsed == {}
