from flask import Flask, request, Response
from playwright.async_api import async_playwright

app = Flask(__name__)


async def take_screenshot(url, viewport_width, viewport_height, full_page):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=[
            # 需要设置代理类型，否则默认的代理类型会被反爬禁止访问
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        ])
        page = await browser.new_page(viewport={"width": viewport_width, "height": viewport_height})
        await page.goto(url)
        ss = await page.screenshot(full_page=full_page)
        await browser.close()
        return ss


@app.route('/screenshot', methods=['GET'])
async def screenshot():
    url = request.args.get('url')
    viewport_width = request.args.get('viewport_width', default=1280, type=int)
    viewport_height = request.args.get('viewport_height', default=720, type=int)
    full_page = request.args.get('full_page', default=0, type=int)
    full_page = bool(full_page)

    if not url:
        return '网页链接不能为空', 400

    try:
        # 截取屏幕并保存
        data = await take_screenshot(url, viewport_width, viewport_height, full_page)
        return Response(data, mimetype='image/png')

    except Exception as e:
        return '发生错误，信息：' + str(e), 500


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=14140)
