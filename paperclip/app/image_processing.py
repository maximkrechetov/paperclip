import cv2
import config


# TODO: Crop
# TODO: Конвертация?
# Класс-процессор
class ImageProcessor:
    STORE_DIR = config.STORE_DIR

    def __init__(self, path):
        # common props
        self.full_path = path

        parts = self.full_path.split('.')

        self.path = parts[0]
        self.parts = self.path.split('_')

        # img
        self.img = None

        # image properties
        self._id = None
        self._width = None
        self._height = None
        self._extension = parts[1]

        # actions
        self._actions = []

    # Основной метод
    def process(self):
        self._parse()
        self.img = cv2.imread("{0}{1}.{2}".format(self.STORE_DIR, self._id, self._extension))

        for action in self._actions:
            getattr(self, action, None)()

        cv2.imwrite(self.STORE_DIR + self.full_path, self.img)
        return True

    # Парсинг пути, назначение необходимых процедур
    def _parse(self):
        for part in self.parts:
            # Парсим id
            self._parse_id(part)
            # Парсим размеры
            self._parse_resize(part)

    # Парсинг ID изображения
    def _parse_id(self, part):
        if self._id:
            return
        self._id = part

    # Парсинг размеров изображения, назначение ресайза
    def _parse_resize(self, part):
        if self._width and self._height:
            return

        sides = part.split('x')

        if len(sides) < 2:
            return

        self._width = int(sides[0])
        self._height = int(sides[1])
        self._actions.append('_resize')

    # Ресайз изображения
    def _resize(self):
        original_height, original_width = self.img.shape[:2]
        aspect_ratio = original_height / original_width

        # Сохраняем пропорции
        if aspect_ratio > 1:
            height = self._height
            width = int(height / aspect_ratio)
        elif aspect_ratio == 1.0:
            width = self._width
            height = width
        else:
            width = self._width
            height = int(width * aspect_ratio)

        self.img = cv2.resize(
            self.img,
            (
                width,
                height
            ),
            interpolation=cv2.INTER_LINEAR
        )



