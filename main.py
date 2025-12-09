import asyncio
import atexit
import os
import threading

from flask import Flask, request, Response, send_from_directory

from tool.screenshot import take_screenshot, cleanup_browser

app = Flask(__name__)
app.static_folder = 'web/dist'

# 共享事件循环（避免每次请求创建新循环）
_loop = None
_loop_thread = None


def get_event_loop():
    """获取或创建共享的事件循环"""
    global _loop, _loop_thread

    if _loop is not None and _loop.is_running():
        return _loop

    _loop = asyncio.new_event_loop()

    def run_loop():
        asyncio.set_event_loop(_loop)
        _loop.run_forever()

    _loop_thread = threading.Thread(target=run_loop, daemon=True)
    _loop_thread.start()
    return _loop


def run_async(coro):
    """在共享事件循环中运行协程"""
    loop = get_event_loop()
    future = asyncio.run_coroutine_threadsafe(coro, loop)
    return future.result(timeout=120)


@atexit.register
def cleanup():
    """程序退出时清理资源"""
    global _loop
    if _loop and _loop.is_running():
        asyncio.run_coroutine_threadsafe(cleanup_browser(), _loop).result(timeout=5)
        _loop.call_soon_threadsafe(_loop.stop)


@app.route('/', methods=['GET'])
def index():
    return send_from_directory(app.static_folder, 'index.html')


# 限制同时运行的截图任务数量
max_concurrent_screenshots = int(os.getenv('MAX_CONCURRENT_SCREENSHOTS', 3))
screenshot_semaphore = threading.Semaphore(max_concurrent_screenshots)


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

    with screenshot_semaphore:
        try:
            screenshot_data = run_async(take_screenshot(**params))
            return Response(screenshot_data, mimetype='image/png')
        except Exception as e:
            return f'发生错误，信息：{str(e)}', 500


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=14140)
