# Включение дебага
DEBUG = False

# Путь к папке с фотками
STORE_DIR = '/images/o/'

# Временная папка для хранения конвертируемых фоточек
TMP_DIR = '/tmp/paperclip/'

# Сохранять ли изображения физически после процессинга
SAVE_PROCESSED_IMAGES = False

# Разрешение изначальных изображений
ORIGINAL_EXTENSIONS = ['jpg', 'png']

# Поля для нормализации
NORMALIZE_CANVAS_PX = 20
NORMALIZE_FIELDS_PX = int(NORMALIZE_CANVAS_PX / 2)

# Ограничения для числовых параметров
FIELDS_LIMITS = {
    'width': 1200,
    'height': 1200,
    'quality': 100
}

AWS = {
    'endpoint_url': 'https://s3.e2e4.ru',
    'display_name': "Paperclip application",
    'access_key': "YWEUC6H19MVRACW5VUW3",
    'secret_key': "AZuqpDTT59sQtvLyVnRhRFh7Dk09q1JJfGCyDCdz",
    'original_files_bucket_name': 'original_images',
    'processed_files_bucket_name': 'processed_images'
}
