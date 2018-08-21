import multiprocessing
import json
import os

from kafka import KafkaConsumer
from colorama import Fore, Style

from config import KAFKA_BROKERS, KAFKA_TOPIC, POOL_PROCESSES, TMP_DIR
from image_processing import ImageProcessor


class Consumer:
    def __init__(self):
        self._init_consumer()

    def _init_consumer(self):
        self.consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BROKERS,
            api_version=(0, 10),
            auto_offset_reset='latest',
            enable_auto_commit=False,
            value_deserializer=lambda m: json.loads(m.decode("utf-8"))
        )

    @staticmethod
    def _process_image(image_config):
        return ImageProcessor(image_config).process_with_s3()

    def process(self):
        for message in self.consumer:
            try:
                pool = multiprocessing.Pool(processes=POOL_PROCESSES)
                pool.map(self._process_image, message.value['data']['config'])
                pool.close()
                pool.join()

                os.remove(TMP_DIR + message.value['data']['fileName'])
                print(
                    Fore.GREEN +
                    '[Paperclip] Successfully done: ' +
                    message.value['data']['fileName'] +
                    Style.RESET_ALL
                )
            except Exception as e:
                print(Fore.RED + '[Paperclip] Error: ' + Style.RESET_ALL)
                print(repr(e))
