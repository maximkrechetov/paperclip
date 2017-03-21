from flask import Flask
from flask import send_file
from paperclip.app.image_processing import ImageProcessor
from pathlib import Path
import config

app = Flask(__name__)
app.config.from_object(__name__)
app.config['DEBUG'] = config.DEBUG
app.config['STORE_DIR'] = config.STORE_DIR


"""
Примерный URL:

/1234567_320x240.jpg
"""


@app.route('/<path:path>')
def process(path):
    full_path = app.config['STORE_DIR'] + path
    image_path = Path(full_path)

    # Проверяем файл на наличие
    if image_path.is_file():
        return send_file(full_path, mimetype='image/jpeg')

    img = ImageProcessor(path)
    img.process()
    return send_file(full_path, mimetype='image/jpeg')
