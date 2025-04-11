from flask import Flask, request, Response, send_from_directory

from tool.screenshot import take_screenshot

app = Flask(__name__)
app.static_folder = 'web/dist'


@app.route('/', methods=['GET'])
async def index():
    # 返回 dist/index.html 文件
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def static_file(path):
    return send_from_directory(app.static_folder, path)


@app.route('/screenshot', methods=['GET', 'POST'])
async def screenshot():
    data = request.get_json() if request.is_json else (request.form if request.method == 'POST' else request.args)
    params = {
        'url': data.get('url'),
        'viewport_width': int(data.get('viewport_width', 1280)),
        'viewport_height': int(data.get('viewport_height', 720)),
        'wait_second': int(data.get('wait_second', 0)),
        'element_selector': data.get('element_selector'),
        'full_page': bool(int(data.get('full_page', 0)))
    }

    if not params['url']:
        return '网页链接不能为空', 400

    try:
        screenshot_data = await take_screenshot(**params)
        return Response(screenshot_data, mimetype='image/png')
    except Exception as e:
        return f'发生错误，信息：{str(e)}', 500


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=14140)
