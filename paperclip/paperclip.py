from flask import Flask
from flask import send_file
from flask import abort
from paperclip.app.image_processing import ImageProcessor
from pathlib import Path
import config

app = Flask(__name__)
app.config.from_object(__name__)
app.config['DEBUG'] = config.DEBUG
app.config['STORE_DIR'] = config.STORE_DIR


@app.route('/<path:path>')
def process(path):
    full_path = app.config['STORE_DIR'] + path

    # Проверка на верный URL (наличие расширения)
    try:
        ext = path.split('.')[1]
        mimetype = 'image/' + ext
    except Exception as e:
        print(e)
        abort(404)

    image_path = Path(full_path)

    # Проверяем файл на наличие
    if image_path.is_file():
        return send_file(full_path, mimetype=mimetype)

    try:
        img = ImageProcessor(path)
        img.process()
        return send_file(full_path, mimetype=mimetype)
    except Exception as e:
        print(e)
        abort(404)
