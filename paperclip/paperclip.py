from flask import Flask
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
    print('fomeofmeofmeofef')
    processor.process_with_s3()
    print('omreoignrignoin')
    return '<h2>LOL</h2>'

app.wsgi_app = ProxyFix(app.wsgi_app)
if __name__ == '__main__':
    app.run()
