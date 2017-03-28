import cv2
import config
import os
import glob
import numpy as np
from pathlib import Path
from flask import abort


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
        self._img_path = None

        # image properties
        self._id = None
        self._width = None
        self._height = None
        self._resize = None
        self._quality = None
        self._extension = parts[1]
        self._save_options = self._extension == 'jpg' and [cv2.IMWRITE_JPEG_PROGRESSIVE, 2] or []

        # actions
        self._actions = []

    # Основной метод
    def process(self):
        # Если файл уже имеется, ничего не делаем
        abs_path = self.STORE_DIR + self.full_path
        self._img_path = abs_path

        if Path(abs_path).is_file():
            return

        # Парсим параметры и назначаем действия над картинкой
        self._parse()
        self._assign_actions()

        # Ищем оригинальную картинку по имени
        # Исходим из соглашения, что оригиналы хранятся под именем "%id%.%разрешение%"
        images = glob.glob(os.path.join(self.STORE_DIR, "{0}.*".format(self._id)))
        image = images and images[0]

        if not image:
            abort(404)

        # Никаких действий не требуется, отдаем оригинал
        if not self._actions:
            self._img_path = image
            return

        self.img = cv2.imread(image)

        for action in self._actions:
            getattr(self, action, None)()

        cv2.imwrite(abs_path, self.img, self._save_options)

    # Получить полный путь к созданному изображению
    def get_full_path(self):
        return self._img_path

    # Получить mimetype изображения
    def get_mimetype(self):
        return 'image/' + self._extension

    # Парсинг пути, назначение необходимых процедур
    def _parse(self):
        for part in self.parts:
            for param_name in ['id', 'resize', 'width', 'height', 'quality']:
                self._parse_param(part, param_name)

    # Назначить действия
    def _assign_actions(self):
        if self._resize:
            self._actions.append('_' + self._resize)
        if self._quality:
            self._actions.append('_change_quality')

    # Парсинг параметров
    def _parse_param(self, part, param_name):
        if getattr(self, '_' + param_name):
            return

        values = part.split('-')
        if len(values) < 2:
            abort(400)

        if values[0] == param_name:
            if values[1].isdigit():
                values[1] = int(values[1])
            setattr(self, '_' + param_name, values[1])

    # Получить размеры для ресайза cover
    def _get_sizes_cover(self):
        original_height, original_width = self.img.shape[:2]
        aspect_ratio = original_height / original_width

        # Сохраняем пропорции
        if aspect_ratio > 1:
            width = self._width
            height = int(width * aspect_ratio)
        elif aspect_ratio == 1.0:
            width = self._width
            height = width
        else:
            height = self._height
            width = int(height / aspect_ratio)

        return width, height

    # Получить размеры для ресайза contain
    def _get_sizes_contain(self):
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

        return width, height

    # Создание канвы
    def _create_canvas(self):
        canvas = np.ndarray(shape=(self._height, self._width, 3), dtype=np.uint8)
        canvas[:] = (255, 255, 255)
        return canvas

    # Ресайз изображения
    def _make_resize(self):
        if not self._resize or self._resize not in ['cover', 'contain']:
            return

        width, height = getattr(self, '_get_sizes_' + self._resize)()

        self.img = cv2.resize(
            self.img,
            (
                width,
                height
            ),
            interpolation=cv2.INTER_LINEAR
        )

    # Resize contain
    def _contain(self):
        self._make_resize()
        canvas = self._create_canvas()
        height, width = self.img.shape[:2]

        if height > width:
            offset = int((self._width - width) / 2)
            canvas[0:height, offset:offset + width, :3] = self.img
        elif height < width:
            offset = int((self._height - height) / 2)
            canvas[offset:offset + height, 0:width, :3] = self.img
        else:
            canvas[:height, :width, :3] = self.img

        self.img = canvas

    # Resize cover
    def _cover(self):
        self._make_resize()
        canvas = self._create_canvas()
        height, width = self.img.shape[:2]

        if height > width:
            offset = int((height - self._height) / 2)
            canvas = self.img[offset:offset + self._height, 0:width]
        elif height < width:
            offset = int((width - self._width) / 2)
            canvas = self.img[0:height, offset:offset + self._width]
        else:
            canvas[:height, :width, :3] = self.img

        self.img = canvas

    # Изменение качества
    def _change_quality(self):
        if self._extension == 'jpg':
            self._save_options += [cv2.IMWRITE_JPEG_QUALITY, self._quality]
        elif self._extension == 'webp':
            self._save_options += [int(cv2.IMWRITE_WEBP_QUALITY), self._quality]
        # Выдаем ошибку во всех остальных случаях
        else:
            abort(400)
