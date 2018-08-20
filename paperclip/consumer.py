import multiprocessing
import json

from kafka import KafkaConsumer
from colorama import Fore, Style

from config import KAFKA_BROKERS, KAFKA_TOPIC, POOL_PROCESSES
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
                processed_urls = pool.map(self._process_image, message.value['data']['config'])

                print(processed_urls)

                pool.close()
                pool.join()
                print(Fore.GREEN + '[Paperclip] Successfully done' + Style.RESET_ALL)
            except Exception as e:
                print(Fore.RED + '[Paperclip] Error: ' + e + Style.RESET_ALL)
