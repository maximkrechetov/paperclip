import os
from dotenv import load_dotenv, find_dotenv

env_file = find_dotenv()

if not bool(env_file):
    raise Exception('.env file does not exist.')

load_dotenv(env_file)

# Включение дебага
DEBUG = os.getenv('DEBUG')

# Временная папка для хранения конвертируемых фоточек
TMP_DIR = os.getenv('TMP_DIR')

# Поля для нормализации
NORMALIZE_CANVAS_PX = int(os.getenv('NORMALIZE_CANVAS_PX'))
NORMALIZE_FIELDS_PX_PARAM = int(os.getenv('NORMALIZE_FIELDS_PX_PARAM'))
NORMALIZE_FIELDS_PX = int(NORMALIZE_CANVAS_PX / NORMALIZE_FIELDS_PX_PARAM)

# Ограничения для числовых параметров
FIELDS_LIMITS = {
    'width': int(os.getenv('FIELDS_WIDTH')),
    'height': int(os.getenv('FIELDS_HEIGHT')),
    'quality': int(os.getenv('FIELDS_QUALITY'))
}

# Параметры AWS
AWS = {
    'endpoint_url': os.getenv('AWS_ENDPOINT_URL'),
    'display_name': os.getenv('AWS_DISPLAY_NAME'),
    'access_key': os.getenv('AWS_ACCESS_KEY'),
    'secret_key': os.getenv('AWS_SECRET_KEY'),
    'original_files_bucket_name': os.getenv('AWS_ORIGINAL_FILES_BUCKET_NAME'),
    'processed_files_bucket_name': os.getenv('AWS_PROCESSED_FILES_BUCKET_NAME')
}

# Параметры RabbitMQ
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST')
RABBITMQ_LOGIN = os.getenv('RABBITMQ_LOGIN')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD')
RABBITMQ_INPUT_QUEUE_NAME = os.getenv('RABBITMQ_INPUT_QUEUE_NAME')
RABBITMQ_OUTPUT_QUEUE_NAME = os.getenv('RABBITMQ_OUTPUT_QUEUE_NAME')

# Настройки Kafka
KAFKA_HOST = os.getenv('KAFKA_HOST')
KAFKA_PORT = os.getenv('KAFKA_PORT')
KAFKA_GROUP_ID = os.getenv('KAFKA_GROUP_ID')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC')
KAFKA_TIMEOUT = 500

# Параметры Pool
POOL_PROCESSES = int(os.getenv('POOL_PROCESSES'))
