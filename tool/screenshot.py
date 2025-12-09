import asyncio
import os

from playwright.async_api import async_playwright, Browser, Playwright

# 全局浏览器实例（复用以提升性能）
_playwright: Playwright = None
_browser: Browser = None
_browser_lock = asyncio.Lock()


async def get_browser():
    """获取或创建浏览器实例（单例模式）"""
    global _playwright, _browser

    # 如果浏览器已存在且连接正常，直接返回
    if _browser is not None and _browser.is_connected():
        return _browser

    # 使用锁防止并发创建多个浏览器实例
    async with _browser_lock:
        # 双重检查
        if _browser is not None and _browser.is_connected():
            return _browser

        # 清理旧实例
        await cleanup_browser()

        args = [
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            '--disable-dev-shm-usage',  # 减少内存使用
            '--no-sandbox',
        ]

        _playwright = await async_playwright().start()
        _browser = await _playwright.chromium.launch(headless=True, args=args)
        return _browser


async def cleanup_browser():
    """清理浏览器资源"""
    global _playwright, _browser
    if _browser:
        try:
            await _browser.close()
        except:
            pass
        _browser = None
    if _playwright:
        try:
            await _playwright.stop()
        except:
            pass
        _playwright = None


async def take_screenshot(url, viewport_width, viewport_height, full_page, wait_second, element_selector=None,
                          use_proxy=False):
    # 获取复用的浏览器实例
    browser = await get_browser()

    # 构建代理配置
    proxy_config = None
    proxy_server = os.getenv("PROXY_SERVER")
    if proxy_server and use_proxy:
        proxy_config = {"server": proxy_server}

    context = None
    try:
        # 每次创建新的 context（轻量级操作）
        context = await browser.new_context(
            locale='zh-CN',
            viewport={"width": viewport_width, "height": viewport_height},
            proxy=proxy_config,
        )
        page = await context.new_page()

        # 检测是否为HTML代码
        if url.strip().startswith(('<html', '<!DOCTYPE html')):
            await page.set_content(url)
        else:
            await page.goto(url)

        if wait_second > 0:
            await page.wait_for_timeout(wait_second * 1000)

        if element_selector:
            element = page.locator(element_selector)
            ss = await element.screenshot()
        else:
            ss = await page.screenshot(full_page=full_page)
        return ss
    except BaseException as e:
        # 如果浏览器崩溃，标记需要重建
        if _browser and not _browser.is_connected():
            await cleanup_browser()
        raise Exception(f"截图失败: {str(e)}")
    finally:
        if context:
            try:
                await context.close()
            except:
                pass
