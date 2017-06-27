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

    if config.SAVE_PROCESSED_IMAGES:
        processor.process_with_save()
        return send_file(processor.get_full_path(), mimetype=processor.get_mimetype())

    processor.process_without_save()
    response = make_response(processor.buffer.tobytes())
    response.headers['Content-Type'] = processor.get_mimetype()
    return response

app.wsgi_app = ProxyFix(app.wsgi_app)
if __name__ == '__main__':
    app.run()