# Включение дебага
DEBUG = False

# Путь к папке с фотками
STORE_DIR = '/images/o/'

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
