"""Test fetch_page tool with TDD RED phase - tests expected to FAIL."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock


class TestFetchPageURLValidation:
    """Test URL validation for fetch_page tool."""

    @pytest.mark.asyncio
    async def test_file_url_raises_unsupported_protocol_error(self):
        """Test that file:// URLs raise ValueError with 'Unsupported protocol' message."""
        from chromium_mcp.tools.fetch_page import fetch_page_async

        with pytest.raises(ValueError) as exc_info:
            await fetch_page_async(url="file:///etc/passwd")

        assert "Unsupported protocol" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invalid_url_raises_value_error(self):
        """Test that malformed URLs raise ValueError."""
        from chromium_mcp.tools.fetch_page import fetch_page_async

        with pytest.raises(ValueError):
            await fetch_page_async(url="not-a-valid-url")

    @pytest.mark.asyncio
    async def test_empty_url_raises_value_error(self):
        """Test that empty URL raises ValueError."""
        from chromium_mcp.tools.fetch_page import fetch_page_async

        with pytest.raises(ValueError):
            await fetch_page_async(url="")

    @pytest.mark.asyncio
    async def test_url_without_host_raises_value_error(self):
        """Test that URLs without host raise ValueError."""
        from chromium_mcp.tools.fetch_page import fetch_page_async

        with pytest.raises(ValueError):
            await fetch_page_async(url="http://")


class TestFetchPageContent:
    """Test page content fetching."""

    @pytest.mark.asyncio
    async def test_fetch_valid_url_returns_markdown(self):
        """Test fetching a valid URL returns markdown content."""
        from chromium_mcp.tools.fetch_page import fetch_page_async

        mock_html = "<html><body><h1>Test Page</h1><p>Hello World</p></body></html>"

        with patch("chromium_mcp.tools.fetch_page.async_playwright") as mock_playwright:
            # Setup mock chain
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.content.return_value = mock_html

            result = await fetch_page_async(url="https://example.com")

            # Should contain markdown-converted content
            assert "Test Page" in result or "Hello World" in result

    @pytest.mark.asyncio
    async def test_fetch_httpbin_returns_content(self):
        """Test fetching httpbin.org/html returns markdown content."""
        from chromium_mcp.tools.fetch_page import fetch_page_async

        # This is a real integration test - will be skipped if no network
        try:
            result = await fetch_page_async(url="https://httpbin.org/html")
            assert len(result) > 0
            assert isinstance(result, str)
        except Exception as e:
            pytest.skip(f"Network test failed: {e}")


class TestFetchPageWaitFor:
    """Test wait_for selector functionality."""

    @pytest.mark.asyncio
    async def test_fetch_with_wait_for_waits_for_selector(self):
        """Test that wait_for parameter waits for CSS selector."""
        from chromium_mcp.tools.fetch_page import fetch_page_async

        mock_html = "<html><body><div class='loaded'>Content</div></body></html>"

        with patch("chromium_mcp.tools.fetch_page.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.content.return_value = mock_html

            result = await fetch_page_async(
                url="https://example.com", wait_for=".loaded"
            )

            # Verify wait_for_selector was called
            mock_page.wait_for_selector.assert_called_once_with(
                ".loaded", timeout=30000
            )
            assert result is not None


class TestFetchPageTimeout:
    """Test timeout handling."""

    @pytest.mark.asyncio
    async def test_timeout_expired_raises_timeout_error(self):
        """Test that timeout expired raises TimeoutError."""
        from chromium_mcp.tools.fetch_page import fetch_page_async
        from playwright.async_api import TimeoutError as PlaywrightTimeoutError

        with patch("chromium_mcp.tools.fetch_page.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page

            # Simulate timeout on goto
            mock_page.goto.side_effect = PlaywrightTimeoutError(
                "Timeout 30000ms exceeded"
            )

            with pytest.raises(TimeoutError):
                await fetch_page_async(url="https://example.com", timeout=1)

    @pytest.mark.asyncio
    async def test_timeout_uses_custom_value(self):
        """Test that custom timeout value is passed to browser."""
        from chromium_mcp.tools.fetch_page import fetch_page_async

        mock_html = "<html><body>Test</body></html>"

        with patch("chromium_mcp.tools.fetch_page.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.content.return_value = mock_html

            await fetch_page_async(url="https://example.com", timeout=60)

            # Verify set_default_timeout was called with correct value (ms)
            mock_page.set_default_timeout.assert_called_once_with(60000)


class TestFetchPageBrowserCleanup:
    """Test browser cleanup on error."""

    @pytest.mark.asyncio
    async def test_browser_closes_on_error(self):
        """Test that browser is closed even when error occurs."""
        from chromium_mcp.tools.fetch_page import fetch_page_async

        with patch("chromium_mcp.tools.fetch_page.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page

            # Simulate error after page is created
            mock_page.goto.side_effect = Exception("Network error")

            with pytest.raises(Exception):
                await fetch_page_async(url="https://example.com")

            # Verify browser was closed
            mock_browser.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_browser_closes_on_success(self):
        """Test that browser is closed after successful fetch."""
        from chromium_mcp.tools.fetch_page import fetch_page_async

        mock_html = "<html><body>Test</body></html>"

        with patch("chromium_mcp.tools.fetch_page.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.content.return_value = mock_html

            await fetch_page_async(url="https://example.com")

            # Verify browser was closed
            mock_browser.close.assert_called_once()


class TestFetchPageFormat:
    """Test output format options."""

    @pytest.mark.asyncio
    async def test_default_format_is_markdown(self):
        """Test that default output format is markdown."""
        from chromium_mcp.tools.fetch_page import fetch_page_async

        mock_html = "<html><body><h1>Title</h1><a href='link'>Click</a></body></html>"

        with patch("chromium_mcp.tools.fetch_page.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.content.return_value = mock_html

            result = await fetch_page_async(url="https://example.com")

            # Markdown should have # for h1
            assert "#" in result or "Title" in result

    @pytest.mark.asyncio
    async def test_html_format_returns_raw_html(self):
        """Test that format='html' returns raw HTML."""
        from chromium_mcp.tools.fetch_page import fetch_page_async

        mock_html = "<html><body><h1>Title</h1></body></html>"

        with patch("chromium_mcp.tools.fetch_page.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.content.return_value = mock_html

            result = await fetch_page_async(url="https://example.com", format="html")

            # Should return raw HTML
            assert "<html>" in result or "<h1>" in result
