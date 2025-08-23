import os

from playwright.async_api import async_playwright


async def take_screenshot(url, viewport_width, viewport_height, full_page, wait_second, element_selector=None,
                          use_proxy=False):
    args = [
        # 需要设置代理类型，否则默认的代理类型会被反爬禁止访问
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    ]
    # 从环境变量获取代理（支持环境变量proxy_server）
    proxy_server = os.getenv("PROXY_SERVER")
    if proxy_server and use_proxy:
        args.append(f"--proxy-server={proxy_server}")
    browser = None
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=args)
            context = await browser.new_context(
                # 设置浏览器语言为简体中文
                locale='zh-CN',
                # 设置浏览器视窗大小
                viewport={"width": viewport_width, "height": viewport_height},
            )
            page = await context.new_page()

            # 检测是否为HTML代码
            if url.strip().startswith(('<html', '<!DOCTYPE html')):
                await page.set_content(url)
            else:
                await page.goto(url)

            if wait_second > 0:
                # 有些页面需要异步加载数据，这里可以设置等待几秒后再截图
                await page.wait_for_timeout(wait_second * 1000)

            if element_selector:
                # 截图指定元素
                element = page.locator(element_selector)
                ss = await element.screenshot()
            else:
                # 截图整个页面
                ss = await page.screenshot(full_page=full_page)
            return ss
    except Exception as e:
        raise Exception(f"截图失败: {str(e)}")
    finally:
        if browser:
            try:
                await browser.close()
            except:
                pass  # 忽略关闭时的错误
