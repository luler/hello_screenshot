from flask import Flask, request, Response
from playwright.async_api import async_playwright

app = Flask(__name__)


async def take_screenshot(url, viewport_width, viewport_height, full_page, wait_second):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=[
            # 需要设置代理类型，否则默认的代理类型会被反爬禁止访问
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        ])
        context = await browser.new_context(
            # 设置浏览器语言为简体中文
            locale='zh-CN',
            # 设置浏览器视窗大小
            viewport={"width": viewport_width, "height": viewport_height},
        )
        page = await context.new_page()
        await page.goto(url)
        if wait_second > 0:
            # 有些页面需要异步加载数据，这里可以设置等待几秒后再截图
            await page.wait_for_timeout(wait_second * 1000)
        ss = await page.screenshot(full_page=full_page)
        await browser.close()
        return ss


@app.route('/screenshot', methods=['GET'])
async def screenshot():
    url = request.args.get('url')
    viewport_width = request.args.get('viewport_width', default=1280, type=int)
    viewport_height = request.args.get('viewport_height', default=720, type=int)
    wait_second = request.args.get('wait_second', default=0, type=int)
    full_page = request.args.get('full_page', default=0, type=int)
    full_page = bool(full_page)

    if not url:
        return '网页链接不能为空', 400

    try:
        # 截取屏幕并保存
        data = await take_screenshot(url, viewport_width, viewport_height, full_page, wait_second)
        return Response(data, mimetype='image/png')

    except Exception as e:
        return '发生错误，信息：' + str(e), 500


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=14140)
