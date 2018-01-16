import cv2
import config
import os
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

        # Свойства для стриминга
        self.buffer = None
        self.retval = None

        # Изображение
        self.img = None
        # Путь к сохраняемому изображению
        self._img_path = None

        # Свойства изображения
        # id
        self._id = None
        # Ширина
        self._width = None
        # Высота
        self._height = None
        # Количество каналов
        self._channels = 3
        # Тип ресайза
        self._resize = None
        # Качество для сохранения
        self._quality = None
        # Расширение для сохранения
        self._extension = parts[1]
        # Опции сохранения
        self._save_options = self._extension == 'jpg' and [cv2.IMWRITE_JPEG_PROGRESSIVE, 2] or []

        # Массив действий для сохранения
        self._actions = []

    # Основной метод без сохранения
    def process_without_save(self):
        # Парсим параметры и назначаем действия над картинкой
        self._parse()
        self._assign_actions()

        # Ищем оригинальную картинку по имени
        # Исходим из соглашения, что оригиналы хранятся под именем "%id%.%разрешение%"
        img_path = self._get_original_img_path()

        # Если оригинал не найден, отдаем 404
        if not img_path:
            abort(404)

        # Если никаких действий не требуется, отдаем оригинал
        if not self._actions:
            self._img_path = img_path
            return

        self._check_extension(img_path)

        try:
            self.img = cv2.imread(img_path, -1)

            # http://jira.opentech.local/browse/SHOP-919
            # Как оказалось, Ч/Б изображения идут с одним каналом, который при открытии не попадает в tuple.
            # В таком случае присваиваем tuple 1 канал.
            shape = self.img.shape
            self._channels = (len(shape) > 2) and shape[-1] or 1
        except:
            abort(404)

        for action in self._actions:
            getattr(self, action, None)()

        retval, buffer = cv2.imencode('.' + self._extension, self.img)
        self.retval = retval
        self.buffer = buffer

    # Основной метод с сохранением
    def process_with_save(self):
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
        img_path = self._get_original_img_path()

        if not img_path:
            abort(404)

        # Никаких действий не требуется, отдаем оригинал
        if not self._actions:
            self._img_path = img_path
            return

        self._check_extension(img_path)

        try:
            self.img = cv2.imread(img_path)
        except:
            abort(404)

        for action in self._actions:
            getattr(self, action, None)()

        cv2.imwrite(abs_path, self.img, self._save_options)

    # Получить полный путь к созданному изображению
    def get_full_path(self):
        return self._img_path

    # Получить mimetype изображения
    def get_mimetype(self):
        return 'image/' + self._extension

    # Не конвертируем png в jpg из-за проблем с прозрачностью
    def _check_extension(self, img_path):
        if img_path.endswith('.png'):
            self._extension = 'png'

    # Получить путь к изображению
    def _get_original_img_path(self):
        img_path = None

        for ext in config.ORIGINAL_EXTENSIONS:
            path = os.path.join(self.STORE_DIR, "{0}.{1}".format(self._id, ext))
            if not Path(path).is_file():
                continue
            img_path = path

        return img_path

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
        canvas = np.ndarray(shape=(self._height, self._width, self._channels), dtype=np.uint8)
        canvas[:] = tuple([255] * self._channels)
        return canvas

    # Проверка self.img.shape, так как shape после действия пересобирается cv
    def _check_img_shape(self):
        if len(self.img.shape) == 2:
            self.img.shape += (1, )

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
        self._check_img_shape()
        canvas = self._create_canvas()
        height, width = self.img.shape[:2]

        if height > width:
            offset = abs(int((self._width - width) / 2))
            canvas[0:height, offset:offset + width, :self._channels] = self.img
        elif height < width:
            offset = abs(int((self._height - height) / 2))
            canvas[offset:offset + height, 0:width, :self._channels] = self.img
        else:
            canvas[:height, :width, :self._channels] = self.img

        self.img = canvas

    # Resize cover
    def _cover(self):
        self._make_resize()
        self._check_img_shape()
        canvas = self._create_canvas()
        height, width = self.img.shape[:2]

        if height > width:
            offset = abs(int((height - self._height) / 2))
            canvas = self.img[offset:offset + self._height, 0:width]
        elif height < width:
            offset = abs(int((width - self._width) / 2))
            canvas = self.img[0:height, offset:offset + self._width]
        else:
            canvas[:height, :width, :self._channels] = self.img

        self.img = canvas

    # Изменение качества
    def _change_quality(self):
        if self._extension == 'jpg':
            self._save_options += [cv2.IMWRITE_JPEG_QUALITY, self._quality]
        elif self._extension == 'webp':
            self._save_options += [int(cv2.IMWRITE_WEBP_QUALITY), self._quality]
        elif self._extension == 'png':
            pass
        # Выдаем ошибку во всех остальных случаях
        else:
            abort(400)
