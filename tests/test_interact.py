"""Test interact tool with TDD RED phase - tests expected to FAIL."""

import pytest
from unittest.mock import AsyncMock, patch


class TestInteractURLValidation:
    """Test URL validation for interact tool."""

    @pytest.mark.asyncio
    async def test_file_url_raises_unsupported_protocol_error(self):
        """Test that file:// URLs raise ValueError with 'Unsupported protocol' message."""
        from chromium_mcp.tools.interact import interact_async

        with pytest.raises(ValueError) as exc_info:
            await interact_async(
                url="file:///etc/passwd",
                actions=[{"type": "click", "selector": "button"}],
            )

        assert "Unsupported protocol" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invalid_url_raises_value_error(self):
        """Test that malformed URLs raise ValueError."""
        from chromium_mcp.tools.interact import interact_async

        with pytest.raises(ValueError):
            await interact_async(
                url="not-a-valid-url", actions=[{"type": "click", "selector": "button"}]
            )

    @pytest.mark.asyncio
    async def test_empty_url_raises_value_error(self):
        """Test that empty URL raises ValueError."""
        from chromium_mcp.tools.interact import interact_async

        with pytest.raises(ValueError):
            await interact_async(
                url="", actions=[{"type": "click", "selector": "button"}]
            )


class TestInteractActionValidation:
    """Test action validation for interact tool."""

    @pytest.mark.asyncio
    async def test_invalid_action_type_raises_value_error(self):
        """Test that invalid action type raises ValueError."""
        from chromium_mcp.tools.interact import interact_async

        with pytest.raises(ValueError) as exc_info:
            await interact_async(
                url="https://example.com", actions=[{"type": "invalid_action"}]
            )

        assert "Invalid action type" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_empty_actions_raises_value_error(self):
        """Test that empty actions list raises ValueError."""
        from chromium_mcp.tools.interact import interact_async

        with pytest.raises(ValueError):
            await interact_async(url="https://example.com", actions=[])


class TestInteractClickAction:
    """Test click action functionality."""

    @pytest.mark.asyncio
    async def test_click_action_calls_page_click(self):
        """Test that click action calls page.click with correct selector."""
        from chromium_mcp.tools.interact import interact_async

        mock_html = "<html><body><button>Clicked</button></body></html>"

        with patch("chromium_mcp.tools.interact.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.content.return_value = mock_html

            await interact_async(
                url="https://example.com",
                actions=[{"type": "click", "selector": "button.submit"}],
            )

            mock_page.click.assert_called_once_with("button.submit")

    @pytest.mark.asyncio
    async def test_click_action_returns_page_content(self):
        """Test that click action returns final page content as markdown."""
        from chromium_mcp.tools.interact import interact_async

        mock_html = "<html><body><h1>Result</h1><p>Action completed</p></body></html>"

        with patch("chromium_mcp.tools.interact.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.content.return_value = mock_html

            result = await interact_async(
                url="https://example.com",
                actions=[{"type": "click", "selector": "button"}],
            )

            assert "Result" in result or "Action completed" in result


class TestInteractFillAction:
    """Test fill action functionality."""

    @pytest.mark.asyncio
    async def test_fill_action_calls_page_fill(self):
        """Test that fill action calls page.fill with correct selector and value."""
        from chromium_mcp.tools.interact import interact_async

        mock_html = "<html><body><input type='text' /></body></html>"

        with patch("chromium_mcp.tools.interact.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.content.return_value = mock_html

            await interact_async(
                url="https://example.com",
                actions=[
                    {
                        "type": "fill",
                        "selector": "input[name='email']",
                        "value": "test@example.com",
                    }
                ],
            )

            mock_page.fill.assert_called_once_with(
                "input[name='email']", "test@example.com"
            )


class TestInteractSelectAction:
    """Test select action functionality."""

    @pytest.mark.asyncio
    async def test_select_action_calls_page_select_option(self):
        """Test that select action calls page.select_option with correct selector and value."""
        from chromium_mcp.tools.interact import interact_async

        mock_html = "<html><body><select><option>US</option></select></body></html>"

        with patch("chromium_mcp.tools.interact.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.content.return_value = mock_html

            await interact_async(
                url="https://example.com",
                actions=[
                    {"type": "select", "selector": "select#country", "value": "US"}
                ],
            )

            mock_page.select_option.assert_called_once_with("select#country", "US")


class TestInteractScrollAction:
    """Test scroll action functionality."""

    @pytest.mark.asyncio
    async def test_scroll_down_action_calls_evaluate(self):
        """Test that scroll down action calls page.evaluate with correct scroll amount."""
        from chromium_mcp.tools.interact import interact_async

        mock_html = "<html><body><div>Long content</div></body></html>"

        with patch("chromium_mcp.tools.interact.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.content.return_value = mock_html

            await interact_async(
                url="https://example.com",
                actions=[{"type": "scroll", "direction": "down", "amount": 500}],
            )

            mock_page.evaluate.assert_called_once_with("window.scrollBy(0, 500)")

    @pytest.mark.asyncio
    async def test_scroll_up_action_calls_evaluate(self):
        """Test that scroll up action calls page.evaluate with negative scroll."""
        from chromium_mcp.tools.interact import interact_async

        mock_html = "<html><body><div>Content</div></body></html>"

        with patch("chromium_mcp.tools.interact.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.content.return_value = mock_html

            await interact_async(
                url="https://example.com",
                actions=[{"type": "scroll", "direction": "up", "amount": 300}],
            )

            mock_page.evaluate.assert_called_once_with("window.scrollBy(0, -300)")


class TestInteractWaitAction:
    """Test wait action functionality."""

    @pytest.mark.asyncio
    async def test_wait_action_calls_wait_for_timeout(self):
        """Test that wait action calls page.wait_for_timeout with correct milliseconds."""
        from chromium_mcp.tools.interact import interact_async

        mock_html = "<html><body>Content</body></html>"

        with patch("chromium_mcp.tools.interact.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.content.return_value = mock_html

            await interact_async(
                url="https://example.com",
                actions=[{"type": "wait", "milliseconds": 1000}],
            )

            mock_page.wait_for_timeout.assert_called_once_with(1000)


class TestInteractActionChain:
    """Test action chain functionality - multiple actions in sequence."""

    @pytest.mark.asyncio
    async def test_action_chain_executes_in_order(self):
        """Test that multiple actions are executed in sequence."""
        from chromium_mcp.tools.interact import interact_async

        mock_html = "<html><body><h1>Final State</h1></body></html>"

        with patch("chromium_mcp.tools.interact.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.content.return_value = mock_html

            await interact_async(
                url="https://example.com",
                actions=[
                    {
                        "type": "fill",
                        "selector": "input[name='email']",
                        "value": "test@test.com",
                    },
                    {
                        "type": "fill",
                        "selector": "input[name='pass']",
                        "value": "secret",
                    },
                    {"type": "click", "selector": "button[type='submit']"},
                ],
            )

            # Verify actions called in order
            assert mock_page.fill.call_count == 2
            mock_page.fill.assert_any_call("input[name='email']", "test@test.com")
            mock_page.fill.assert_any_call("input[name='pass']", "secret")
            mock_page.click.assert_called_once_with("button[type='submit']")

    @pytest.mark.asyncio
    async def test_action_chain_returns_final_content(self):
        """Test that action chain returns final page content after all actions."""
        from chromium_mcp.tools.interact import interact_async

        mock_html = "<html><body><h1>Submitted</h1><p>Thank you</p></body></html>"

        with patch("chromium_mcp.tools.interact.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.content.return_value = mock_html

            result = await interact_async(
                url="https://example.com",
                actions=[
                    {"type": "click", "selector": "button"},
                    {"type": "wait", "milliseconds": 500},
                ],
            )

            assert "Submitted" in result or "Thank you" in result


class TestInteractBrowserCleanup:
    """Test browser cleanup on error."""

    @pytest.mark.asyncio
    async def test_browser_closes_on_error(self):
        """Test that browser is closed even when error occurs during action."""
        from chromium_mcp.tools.interact import interact_async

        with patch("chromium_mcp.tools.interact.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page

            # Simulate error during click
            mock_page.click.side_effect = Exception("Element not found")

            with pytest.raises(Exception):
                await interact_async(
                    url="https://example.com",
                    actions=[{"type": "click", "selector": "button"}],
                )

            # Verify browser was closed
            mock_browser.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_browser_closes_on_success(self):
        """Test that browser is closed after successful interaction."""
        from chromium_mcp.tools.interact import interact_async

        mock_html = "<html><body>Done</body></html>"

        with patch("chromium_mcp.tools.interact.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.content.return_value = mock_html

            await interact_async(
                url="https://example.com",
                actions=[{"type": "click", "selector": "button"}],
            )

            # Verify browser was closed
            mock_browser.close.assert_called_once()


class TestInteractTimeout:
    """Test timeout handling."""

    @pytest.mark.asyncio
    async def test_timeout_expired_raises_timeout_error(self):
        """Test that timeout expired raises TimeoutError."""
        from chromium_mcp.tools.interact import interact_async
        from playwright.async_api import TimeoutError as PlaywrightTimeoutError

        with patch("chromium_mcp.tools.interact.async_playwright") as mock_playwright:
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
                await interact_async(
                    url="https://example.com",
                    actions=[{"type": "click", "selector": "button"}],
                    timeout=1,
                )

    @pytest.mark.asyncio
    async def test_timeout_uses_custom_value(self):
        """Test that custom timeout value is passed to browser."""
        from chromium_mcp.tools.interact import interact_async

        mock_html = "<html><body>Test</body></html>"

        with patch("chromium_mcp.tools.interact.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value = mock_pw
            mock_pw.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.content.return_value = mock_html

            await interact_async(
                url="https://example.com",
                actions=[{"type": "click", "selector": "button"}],
                timeout=60,
            )

            # Verify set_default_timeout was called with correct value (ms)
            mock_page.set_default_timeout.assert_called_once_with(60000)
