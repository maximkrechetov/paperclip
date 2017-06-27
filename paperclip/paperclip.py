from flask import Flask
from flask import send_file, make_response
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
    if config.SAVE_PROCESSED_IMAGES:
        return send_file(processor.get_full_path(), mimetype=processor.get_mimetype())

    response = make_response(processor.buffer.tobytes())
    response.headers['Content-Type'] = processor.get_mimetype()
    return response

app.wsgi_app = ProxyFix(app.wsgi_app)
if __name__ == '__main__':
    app.run()