# Включение дебага
DEBUG = False

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
    'width': 1700,
    'height': 1700,
    'quality': 100
}

# Параметры AWS
AWS = {
    'endpoint_url': 'https://s3.e2e4.ru',
    'display_name': "Paperclip application",
    'access_key': "YWEUC6H19MVRACW5VUW3",
    'secret_key': "AZuqpDTT59sQtvLyVnRhRFh7Dk09q1JJfGCyDCdz",
    'original_files_bucket_name': 'images_originals',
    'processed_files_bucket_name': 'images_converted'
}

# Параметры RabbitMQ
RABBITMQ_HOST = '100.100.104.240'
RABBITMQ_LOGIN = 'admin'
RABBITMQ_PASSWORD = 'password'
RABBITMQ_INPUT_QUEUE_NAME = 'images_to_convert'
RABBITMQ_OUTPUT_QUEUE_NAME = 'images_converted'

# Параметры Pool
POOL_PROCESSES = 8
