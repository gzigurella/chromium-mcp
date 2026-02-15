"""Test get_link tool with TDD."""

import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock


def create_mock_locator():
    """Helper to create a properly mocked Playwright locator."""
    locator = MagicMock()
    locator.text_content = AsyncMock()
    locator.get_attribute = AsyncMock()
    locator.count = AsyncMock()
    locator.click = AsyncMock()
    locator.nth = MagicMock()
    return locator


def create_mock_page():
    """Helper to create a properly mocked Playwright page."""
    page = MagicMock()
    page.goto = AsyncMock()
    page.content = AsyncMock()
    page.url = "https://example.com"
    page.set_default_timeout = MagicMock()
    page.locator = MagicMock()
    page.wait_for_load_state = AsyncMock()
    page.expect_navigation = MagicMock()
    return page


class TestGetLinkURLValidation:
    """Test URL validation for get_link tool."""

    @pytest.mark.asyncio
    async def test_file_url_raises_unsupported_protocol_error(self):
        """Test that file:// URLs raise ValueError with 'Unsupported protocol' message."""
        from chromium_mcp.tools.get_link import get_link_async

        with pytest.raises(ValueError) as exc_info:
            await get_link_async(url="file:///etc/passwd", selector="a.download")

        assert "Unsupported protocol" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invalid_url_raises_value_error(self):
        """Test that malformed URLs raise ValueError."""
        from chromium_mcp.tools.get_link import get_link_async

        with pytest.raises(ValueError):
            await get_link_async(url="not-a-valid-url", selector="a")

    @pytest.mark.asyncio
    async def test_empty_url_raises_value_error(self):
        """Test that empty URL raises ValueError."""
        from chromium_mcp.tools.get_link import get_link_async

        with pytest.raises(ValueError):
            await get_link_async(url="", selector="a")

    @pytest.mark.asyncio
    async def test_url_without_host_raises_value_error(self):
        """Test that URLs without host raise ValueError."""
        from chromium_mcp.tools.get_link import get_link_async

        with pytest.raises(ValueError):
            await get_link_async(url="http://", selector="a")


class TestGetLinkWithoutClick:
    """Test get_link without clicking (default behavior)."""

    @pytest.mark.asyncio
    async def test_get_link_returns_href_and_text(self):
        """Test that get_link returns href and text without clicking."""
        from chromium_mcp.tools.get_link import get_link_async

        with patch("chromium_mcp.tools.get_link.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = create_mock_page()
            mock_locator = create_mock_locator()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.locator.return_value = mock_locator
            mock_locator.get_attribute.return_value = "https://example.com/file.pdf"
            mock_locator.text_content.return_value = "Download PDF"

            result = await get_link_async(
                url="https://example.com", selector="a.download"
            )

            parsed = json.loads(result)
            assert parsed["href"] == "https://example.com/file.pdf"
            assert parsed["text"] == "Download PDF"
            assert "final_url" not in parsed

    @pytest.mark.asyncio
    async def test_get_link_does_not_click_by_default(self):
        """Test that get_link does not click when click=False (default)."""
        from chromium_mcp.tools.get_link import get_link_async

        with patch("chromium_mcp.tools.get_link.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = create_mock_page()
            mock_locator = create_mock_locator()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.locator.return_value = mock_locator
            mock_locator.get_attribute.return_value = "https://example.com/page"
            mock_locator.text_content.return_value = "Link"

            await get_link_async(url="https://example.com", selector="a.link")

            # Click should NOT be called when click=False (default)
            mock_locator.click.assert_not_called()


class TestGetLinkWithClick:
    """Test get_link with click=true."""

    @pytest.mark.asyncio
    async def test_get_link_click_returns_final_url(self):
        """Test that get_link with click=true returns final_url after navigation."""
        from chromium_mcp.tools.get_link import get_link_async

        with patch("chromium_mcp.tools.get_link.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = create_mock_page()
            mock_locator = create_mock_locator()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.locator.return_value = mock_locator
            mock_locator.get_attribute.return_value = "https://example.com/file.pdf"
            mock_locator.text_content.return_value = "Download"

            # Mock navigation - set final URL after click
            mock_page.url = "https://cdn.example.com/real-file.pdf"

            # Mock expect_navigation context manager
            mock_nav_context = AsyncMock()
            mock_response_info = MagicMock()
            mock_response_info.value = AsyncMock()
            mock_nav_context.__aenter__.return_value = mock_response_info
            mock_nav_context.__aexit__.return_value = None
            mock_page.expect_navigation.return_value = mock_nav_context

            result = await get_link_async(
                url="https://example.com", selector="a.download", click=True
            )

            parsed = json.loads(result)
            assert parsed["href"] == "https://example.com/file.pdf"
            assert parsed["text"] == "Download"
            assert parsed["final_url"] == "https://cdn.example.com/real-file.pdf"

    @pytest.mark.asyncio
    async def test_get_link_click_waits_for_navigation(self):
        """Test that get_link with click=true waits for page load."""
        from chromium_mcp.tools.get_link import get_link_async

        with patch("chromium_mcp.tools.get_link.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = create_mock_page()
            mock_locator = create_mock_locator()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.locator.return_value = mock_locator
            mock_locator.get_attribute.return_value = "https://example.com/page"
            mock_locator.text_content.return_value = "Link"

            # Mock navigation
            mock_nav_context = AsyncMock()
            mock_response_info = MagicMock()
            mock_response_info.value = AsyncMock()
            mock_nav_context.__aenter__.return_value = mock_response_info
            mock_nav_context.__aexit__.return_value = None
            mock_page.expect_navigation.return_value = mock_nav_context

            await get_link_async(
                url="https://example.com", selector="a.link", click=True
            )

            # Verify expect_navigation was used
            mock_page.expect_navigation.assert_called_once()


class TestGetLinkSelectorNotFound:
    """Test handling of selector not found."""

    @pytest.mark.asyncio
    async def test_selector_not_found_raises_error(self):
        """Test that selector not found raises ValueError."""
        from chromium_mcp.tools.get_link import get_link_async

        with patch("chromium_mcp.tools.get_link.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = create_mock_page()
            mock_locator = create_mock_locator()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.locator.return_value = mock_locator
            mock_locator.get_attribute.return_value = None
            mock_locator.text_content.return_value = None

            # This should raise ValueError when element not found
            with pytest.raises(ValueError) as exc_info:
                await get_link_async(url="https://example.com", selector=".nonexistent")

            assert "not found" in str(exc_info.value).lower()


class TestGetLinkTimeout:
    """Test timeout handling."""

    @pytest.mark.asyncio
    async def test_timeout_expired_raises_timeout_error(self):
        """Test that timeout expired raises TimeoutError."""
        from chromium_mcp.tools.get_link import get_link_async
        from playwright.async_api import TimeoutError as PlaywrightTimeoutError

        with patch("chromium_mcp.tools.get_link.async_playwright") as mock_playwright:
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
                await get_link_async(url="https://example.com", selector="a", timeout=1)

    @pytest.mark.asyncio
    async def test_timeout_uses_custom_value(self):
        """Test that custom timeout value is passed to browser."""
        from chromium_mcp.tools.get_link import get_link_async

        with patch("chromium_mcp.tools.get_link.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = create_mock_page()
            mock_locator = create_mock_locator()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.locator.return_value = mock_locator
            mock_locator.get_attribute.return_value = "https://example.com/link"
            mock_locator.text_content.return_value = "Link"

            await get_link_async(url="https://example.com", selector="a", timeout=60)

            # Verify set_default_timeout was called with correct value (ms)
            mock_page.set_default_timeout.assert_called_once_with(60000)


class TestGetLinkBrowserCleanup:
    """Test browser cleanup on error."""

    @pytest.mark.asyncio
    async def test_browser_closes_on_error(self):
        """Test that browser is closed even when error occurs."""
        from chromium_mcp.tools.get_link import get_link_async

        with patch("chromium_mcp.tools.get_link.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = create_mock_page()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page

            # Simulate error after page is created
            mock_page.goto.side_effect = Exception("Network error")

            with pytest.raises(Exception):
                await get_link_async(url="https://example.com", selector="a")

            # Verify browser was closed
            mock_browser.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_browser_closes_on_success(self):
        """Test that browser is closed after successful operation."""
        from chromium_mcp.tools.get_link import get_link_async

        with patch("chromium_mcp.tools.get_link.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = create_mock_page()
            mock_locator = create_mock_locator()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.locator.return_value = mock_locator
            mock_locator.get_attribute.return_value = "https://example.com/link"
            mock_locator.text_content.return_value = "Link"

            await get_link_async(url="https://example.com", selector="a")

            # Verify browser was closed
            mock_browser.close.assert_called_once()


class TestGetLinkOutputFormat:
    """Test output format is valid JSON."""

    @pytest.mark.asyncio
    async def test_output_is_valid_json_string(self):
        """Test that output is a valid JSON string."""
        from chromium_mcp.tools.get_link import get_link_async

        with patch("chromium_mcp.tools.get_link.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = create_mock_page()
            mock_locator = create_mock_locator()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.locator.return_value = mock_locator
            mock_locator.get_attribute.return_value = "https://example.com/link"
            mock_locator.text_content.return_value = "Link Text"

            result = await get_link_async(url="https://example.com", selector="a.link")

            # Should be string
            assert isinstance(result, str)
            # Should be valid JSON
            parsed = json.loads(result)
            assert isinstance(parsed, dict)

    @pytest.mark.asyncio
    async def test_text_is_stripped(self):
        """Test that link text is stripped of whitespace."""
        from chromium_mcp.tools.get_link import get_link_async

        with patch("chromium_mcp.tools.get_link.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = create_mock_page()
            mock_locator = create_mock_locator()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.locator.return_value = mock_locator
            mock_locator.get_attribute.return_value = "https://example.com/link"
            mock_locator.text_content.return_value = "  Link Text  "

            result = await get_link_async(url="https://example.com", selector="a.link")

            parsed = json.loads(result)
            assert parsed["text"] == "Link Text"
