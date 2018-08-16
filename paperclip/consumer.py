import multiprocessing
from kafka import KafkaConsumer
from config import KAFKA_HOST, KAFKA_PORT, KAFKA_TIMEOUT, KAFKA_TOPIC


class Consumer(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.stop_event = multiprocessing.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        consumer = KafkaConsumer(bootstrap_servers='{}:{}'.format(KAFKA_HOST, KAFKA_PORT),
                                 api_version=(0, 10),
                                 auto_offset_reset='earliest',
                                 consumer_timeout_ms=KAFKA_TIMEOUT)

        consumer.subscribe([KAFKA_TOPIC])

        while not self.stop_event.is_set():
            for message in consumer:
                print(message)
                if self.stop_event.is_set():
                    break

        consumer.close()
