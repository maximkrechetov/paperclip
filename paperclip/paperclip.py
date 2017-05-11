from flask import Flask
from flask import send_file
from werkzeug.contrib.fixers import ProxyFix
from paperclip.app.image_processing import ImageProcessor
import config

app = Flask(__name__)
app.config.from_object(__name__)
app.config['DEBUG'] = config.DEBUG
app.config['STORE_DIR'] = config.STORE_DIR


@app.route('/<path:path>')
def magic(path):
    processor = ImageProcessor(path)
    processor.process()
    return send_file(processor.get_full_path(), mimetype=processor.get_mimetype())

app.wsgi_app = ProxyFix(app.wsgi_app)
if __name__ == '__main__':
    app.run()