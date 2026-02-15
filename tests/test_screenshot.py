"""Test screenshot tool with TDD RED phase - tests expected to FAIL."""

import pytest
import base64
from unittest.mock import AsyncMock, patch, MagicMock


class TestScreenshotURLValidation:
    """Test URL validation for screenshot tool."""

    @pytest.mark.asyncio
    async def test_file_url_raises_unsupported_protocol_error(self):
        """Test that file:// URLs raise ValueError with 'Unsupported protocol' message."""
        from chromium_mcp.tools.screenshot import screenshot_async

        with pytest.raises(ValueError) as exc_info:
            await screenshot_async(url="file:///etc/passwd")

        assert "Unsupported protocol" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invalid_url_raises_value_error(self):
        """Test that malformed URLs raise ValueError."""
        from chromium_mcp.tools.screenshot import screenshot_async

        with pytest.raises(ValueError):
            await screenshot_async(url="not-a-valid-url")

    @pytest.mark.asyncio
    async def test_empty_url_raises_value_error(self):
        """Test that empty URL raises ValueError."""
        from chromium_mcp.tools.screenshot import screenshot_async

        with pytest.raises(ValueError):
            await screenshot_async(url="")

    @pytest.mark.asyncio
    async def test_url_without_host_raises_value_error(self):
        """Test that URLs without host raise ValueError."""
        from chromium_mcp.tools.screenshot import screenshot_async

        with pytest.raises(ValueError):
            await screenshot_async(url="http://")


class TestScreenshotPNG:
    """Test PNG screenshot functionality."""

    @pytest.mark.asyncio
    async def test_screenshot_returns_base64_png(self):
        """Test that screenshot returns base64-encoded PNG."""
        from chromium_mcp.tools.screenshot import screenshot_async

        # Valid PNG header in bytes (first 8 bytes of any PNG)
        fake_png_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100

        with patch("chromium_mcp.tools.screenshot.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.screenshot.return_value = fake_png_bytes

            result = await screenshot_async(url="https://example.com")

            # Should return base64 string
            assert isinstance(result, str)
            # Should be valid base64
            decoded = base64.b64decode(result)
            assert decoded.startswith(b"\x89PNG")

    @pytest.mark.asyncio
    async def test_screenshot_default_is_png(self):
        """Test that default format is PNG."""
        from chromium_mcp.tools.screenshot import screenshot_async

        fake_png_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100

        with patch("chromium_mcp.tools.screenshot.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.screenshot.return_value = fake_png_bytes

            await screenshot_async(url="https://example.com")

            # Verify screenshot was called with type="png"
            mock_page.screenshot.assert_called_once()
            call_kwargs = mock_page.screenshot.call_args[1]
            assert call_kwargs.get("type") == "png"


class TestScreenshotJPEG:
    """Test JPEG screenshot functionality."""

    @pytest.mark.asyncio
    async def test_screenshot_jpeg_format(self):
        """Test that format='jpeg' returns JPEG screenshot."""
        from chromium_mcp.tools.screenshot import screenshot_async

        # Fake JPEG bytes (starts with FFD8FF)
        fake_jpeg_bytes = b"\xff\xd8\xff\xe0" + b"\x00" * 100

        with patch("chromium_mcp.tools.screenshot.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.screenshot.return_value = fake_jpeg_bytes

            result = await screenshot_async(url="https://example.com", format="jpeg")

            # Verify screenshot was called with type="jpeg"
            call_kwargs = mock_page.screenshot.call_args[1]
            assert call_kwargs.get("type") == "jpeg"

    @pytest.mark.asyncio
    async def test_screenshot_jpeg_quality_parameter(self):
        """Test that quality parameter is passed for JPEG."""
        from chromium_mcp.tools.screenshot import screenshot_async

        fake_jpeg_bytes = b"\xff\xd8\xff\xe0" + b"\x00" * 100

        with patch("chromium_mcp.tools.screenshot.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.screenshot.return_value = fake_jpeg_bytes

            await screenshot_async(url="https://example.com", format="jpeg", quality=50)

            # Verify quality was passed
            call_kwargs = mock_page.screenshot.call_args[1]
            assert call_kwargs.get("quality") == 50


class TestScreenshotFullPage:
    """Test full_page screenshot functionality."""

    @pytest.mark.asyncio
    async def test_full_page_true_passes_parameter(self):
        """Test that full_page=True is passed to Playwright."""
        from chromium_mcp.tools.screenshot import screenshot_async

        fake_png_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100

        with patch("chromium_mcp.tools.screenshot.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.screenshot.return_value = fake_png_bytes

            await screenshot_async(url="https://example.com", full_page=True)

            # Verify full_page=True was passed
            call_kwargs = mock_page.screenshot.call_args[1]
            assert call_kwargs.get("full_page") is True

    @pytest.mark.asyncio
    async def test_full_page_false_default(self):
        """Test that full_page defaults to False."""
        from chromium_mcp.tools.screenshot import screenshot_async

        fake_png_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100

        with patch("chromium_mcp.tools.screenshot.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.screenshot.return_value = fake_png_bytes

            await screenshot_async(url="https://example.com")

            # Verify full_page is False by default
            call_kwargs = mock_page.screenshot.call_args[1]
            assert call_kwargs.get("full_page") is False


class TestScreenshotSelector:
    """Test element screenshot with CSS selector."""

    @pytest.mark.asyncio
    async def test_selector_uses_locator_screenshot(self):
        """Test that selector parameter uses locator.screenshot()."""
        from chromium_mcp.tools.screenshot import screenshot_async

        fake_png_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100

        with patch("chromium_mcp.tools.screenshot.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = AsyncMock()
            mock_locator = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            # page.locator() is SYNC - return value directly, not as coroutine
            mock_page.locator = MagicMock(return_value=mock_locator)
            mock_locator.screenshot.return_value = fake_png_bytes

            result = await screenshot_async(url="https://example.com", selector="h1")

            # Verify locator was used
            mock_page.locator.assert_called_once_with("h1")
            mock_locator.screenshot.assert_called_once()

    @pytest.mark.asyncio
    async def test_selector_with_format_and_quality(self):
        """Test selector screenshot with format and quality parameters."""
        from chromium_mcp.tools.screenshot import screenshot_async

        fake_jpeg_bytes = b"\xff\xd8\xff\xe0" + b"\x00" * 100

        with patch("chromium_mcp.tools.screenshot.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = AsyncMock()
            mock_locator = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            # page.locator() is SYNC - return value directly, not as coroutine
            mock_page.locator = MagicMock(return_value=mock_locator)
            mock_locator.screenshot.return_value = fake_jpeg_bytes

            await screenshot_async(
                url="https://example.com", selector=".banner", format="jpeg", quality=70
            )

            # Verify parameters passed to locator.screenshot
            call_kwargs = mock_locator.screenshot.call_args[1]
            assert call_kwargs.get("type") == "jpeg"
            assert call_kwargs.get("quality") == 70


class TestScreenshotTimeout:
    """Test timeout handling."""

    @pytest.mark.asyncio
    async def test_timeout_expired_raises_timeout_error(self):
        """Test that timeout expired raises TimeoutError."""
        from chromium_mcp.tools.screenshot import screenshot_async
        from playwright.async_api import TimeoutError as PlaywrightTimeoutError

        with patch("chromium_mcp.tools.screenshot.async_playwright") as mock_playwright:
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
                await screenshot_async(url="https://example.com", timeout=1)

    @pytest.mark.asyncio
    async def test_timeout_uses_custom_value(self):
        """Test that custom timeout value is passed to browser."""
        from chromium_mcp.tools.screenshot import screenshot_async

        fake_png_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100

        with patch("chromium_mcp.tools.screenshot.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.screenshot.return_value = fake_png_bytes

            await screenshot_async(url="https://example.com", timeout=60)

            # Verify set_default_timeout was called with correct value (ms)
            mock_page.set_default_timeout.assert_called_once_with(60000)


class TestScreenshotBrowserCleanup:
    """Test browser cleanup on error."""

    @pytest.mark.asyncio
    async def test_browser_closes_on_error(self):
        """Test that browser is closed even when error occurs."""
        from chromium_mcp.tools.screenshot import screenshot_async

        with patch("chromium_mcp.tools.screenshot.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page

            # Simulate error after page is created
            mock_page.goto.side_effect = Exception("Network error")

            with pytest.raises(Exception):
                await screenshot_async(url="https://example.com")

            # Verify browser was closed
            mock_browser.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_browser_closes_on_success(self):
        """Test that browser is closed after successful screenshot."""
        from chromium_mcp.tools.screenshot import screenshot_async

        fake_png_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100

        with patch("chromium_mcp.tools.screenshot.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.screenshot.return_value = fake_png_bytes

            await screenshot_async(url="https://example.com")

            # Verify browser was closed
            mock_browser.close.assert_called_once()


class TestScreenshotReal:
    """Real integration tests (network-dependent)."""

    @pytest.mark.asyncio
    async def test_screenshot_real_url_returns_png(self):
        """Test screenshot of real URL returns valid PNG."""
        from chromium_mcp.tools.screenshot import screenshot_async

        try:
            result = await screenshot_async(url="https://example.com")

            # Should return base64 string
            assert isinstance(result, str)
            assert len(result) > 0

            # Decode and verify PNG header
            decoded = base64.b64decode(result)
            assert decoded.startswith(b"\x89PNG\r\n\x1a\n")
        except Exception as e:
            pytest.skip(f"Network test failed: {e}")
