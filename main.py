import asyncio
import os
import threading  # 改用 threading

from flask import Flask, request, Response, send_from_directory

from tool.screenshot import take_screenshot

app = Flask(__name__)
app.static_folder = 'web/dist'


@app.route('/', methods=['GET'])
def index():
    # 返回 dist/index.html 文件
    return send_from_directory(app.static_folder, 'index.html')


# 限制同时运行的截图任务数量
max_concurrent_screenshots = int(os.getenv('MAX_CONCURRENT_SCREENSHOTS', 3))
screenshot_semaphore = threading.Semaphore(max_concurrent_screenshots)  # ✅ 改用 threading.Semaphore，最多N个并发截图任务


@app.route('/<path:path>')
def static_file(path):
    return send_from_directory(app.static_folder, path)


@app.route('/screenshot', methods=['GET', 'POST'])
def screenshot():
    data = request.get_json() if request.is_json else (request.form if request.method == 'POST' else request.args)
    params = {
        'url': data.get('url'),
        'viewport_width': int(data.get('viewport_width', 1280)),
        'viewport_height': int(data.get('viewport_height', 720)),
        'wait_second': int(data.get('wait_second', 0)),
        'element_selector': data.get('element_selector'),
        'full_page': bool(int(data.get('full_page', 0))),
        'use_proxy': bool(int(data.get('use_proxy', 0)))
    }

    if not params['url']:
        return '网页链接不能为空', 400

    with screenshot_semaphore:  # ✅ 改用 with（不是 async with）
        try:
            screenshot_data = asyncio.run(take_screenshot(**params))
            return Response(screenshot_data, mimetype='image/png')
        except Exception as e:
            return f'发生错误，信息：{str(e)}', 500


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=14140)
