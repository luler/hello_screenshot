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
