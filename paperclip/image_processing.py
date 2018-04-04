import cv2
import os
import numpy as np
from flask import abort
from aws_client import s3
from config import AWS, TMP_DIR, ORIGINAL_EXTENSIONS, \
    NORMALIZE_CANVAS_PX, NORMALIZE_FIELDS_PX, FIELDS_LIMITS


# Класс-процессор
class ImageProcessor:
    ORIGINAL_BUCKET = AWS['original_files_bucket_name']
    PROCESSED_BUCKET = AWS['processed_files_bucket_name']

    def __init__(self, image_id, image_data):
        # Изображение
        self.img = None

        # Свойства изображения
        # id
        self._id = image_id
        # Ширина
        self._width = image_data['width']
        # Высота
        self._height = image_data['height']
        # Количество каналов
        self._channels = 3
        # Тип ресайза
        self._resize = image_data['resize']
        # Качество для сохранения
        self._quality = image_data['quality']
        # Расширение для сохранения
        self._extension = image_data['extension']

        # Путь для сохранения
        self.full_path = 'id-{}_width-{}_height-{}_resize-{}_quality-{}.{}'.format(
            self._id,
            self._width,
            self._height,
            self._resize,
            self._quality,
            self._extension
        )

        print(self.full_path)

        # Опции сохранения
        self._save_options = self._extension == 'jpg' and [cv2.IMWRITE_JPEG_PROGRESSIVE, 2] or []
        # Массив действий для сохранения
        self._actions = ['_normalize_content']

    # Метод с Amazon S3
    def process_with_s3(self):
        try:
            s3.get_object(Bucket=self.PROCESSED_BUCKET,
                          Key=self.full_path)
            return self._get_s3_url(self.PROCESSED_BUCKET,
                                    self.full_path)
        except:
            pass

        # Находим оригинал
        original_img_path, original_tmp_path = self._download_file_from_s3()

        # Назначаем действия над картинкой
        self._assign_actions()

        # Если никаких действий не требуется, отдаем оригинал
        if not self._actions:
            return self._get_s3_url(self.ORIGINAL_BUCKET, original_img_path)

        self._check_extension(original_img_path)

        try:
            self.img = cv2.imread(original_tmp_path, -1)

            # http://jira.opentech.local/browse/SHOP-919
            # Как оказалось, Ч/Б изображения идут с одним каналом, который при открытии не попадает в tuple.
            # В таком случае присваиваем tuple 1 канал.
            shape = self.img.shape
            self._channels = (len(shape) > 2) and shape[-1] or 1
        except:
            abort(404)

        for action in self._actions:
            getattr(self, action, None)()

        # Сохраняем файл, загружаем на s3
        output_file_path = TMP_DIR + self.full_path
        cv2.imwrite(output_file_path, self.img, self._save_options)
        s3.upload_file(output_file_path,
                       self.PROCESSED_BUCKET,
                       self.full_path,
                       {'ContentType': 'image/{}'.format(self._extension)})

        # MAKE S3 OBJECT PUBLIC AGAIN
        s3.put_object_acl(Bucket=self.PROCESSED_BUCKET,
                          Key=self.full_path,
                          ACL="public-read")

        # Чистим файлы
        os.remove(original_tmp_path)
        os.remove(output_file_path)

        return self._get_s3_url(self.PROCESSED_BUCKET, self.full_path)

    # Не конвертируем png в jpg из-за проблем с прозрачностью
    def _check_extension(self, img_path):
        if img_path.endswith('.png'):
            self._extension = 'png'

    # Скачиваем файл в /tmp для конвертации
    def _download_file_from_s3(self):
        for ext in ORIGINAL_EXTENSIONS:
            try:
                path = "{0}.{1}".format(self._id, ext)
                tmp_path = TMP_DIR + path
                s3.download_file(self.ORIGINAL_BUCKET, path, tmp_path)
                return path, tmp_path
            except Exception as e:
                print(e)
                continue

        abort(404)

    # Получить s3 URL для загруженного изображения
    def _get_s3_url(self, bucket, path):
        return '{}/{}/{}'.format(s3.meta.endpoint_url, bucket, path)

    # Назначить действия
    def _assign_actions(self):
        if self._resize:
            self._actions.append('_' + self._resize)
        if self._quality:
            self._actions.append('_change_quality')

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
    def _create_canvas(self, height=None, width=None):
        new_height = height or self._height
        new_width = width or self._width
        canvas = np.ndarray(shape=(new_height, new_width, self._channels), dtype=np.uint8)
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

    # Нормализация контента
    def _normalize_content(self):
        (y, x, _) = np.where(self.img != tuple([255] * self._channels))
        (top_y, top_x) = (np.min(y), np.min(x))
        (bottom_y, bottom_x) = (np.max(y), np.max(x))

        self.img = self.img[top_y:bottom_y, top_x:bottom_x]

        height, width = self.img.shape[:2]
        canvas_px = NORMALIZE_CANVAS_PX
        fields_px = NORMALIZE_FIELDS_PX

        if height < width:
            canvas = self._create_canvas(height, width + canvas_px)
            canvas[:height, fields_px:width + fields_px, :self._channels] = self.img
        elif height > width:
            canvas = self._create_canvas(height + canvas_px, width)
            canvas[fields_px:height + fields_px, :width, :self._channels] = self.img
        else:
            canvas = self._create_canvas(height + canvas_px, width + canvas_px)
            canvas[fields_px:height + fields_px, fields_px:width + fields_px, :self._channels] = self.img

        self.img = canvas
