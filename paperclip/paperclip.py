from flask import Flask, jsonify
from werkzeug.contrib.fixers import ProxyFix
from paperclip.app.image_processing import ImageProcessor
import config

app = Flask(__name__)
app.config.from_object(__name__)
app.config['DEBUG'] = config.DEBUG


@app.route('/<path:path>')
def magic(path):
    processor = ImageProcessor(path)
    processed_url = processor.process_with_s3()
    return jsonify({'url': processed_url})

app.wsgi_app = ProxyFix(app.wsgi_app)
if __name__ == '__main__':
    app.run()
