import threading, time
from kafka import KafkaProducer
from config import KAFKA_HOST, KAFKA_PORT, KAFKA_TOPIC


class Producer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        producer = KafkaProducer(bootstrap_servers='{}:{}'.format(KAFKA_HOST, KAFKA_PORT), api_version=(0, 10))

        while not self.stop_event.is_set():
            producer.send(KAFKA_TOPIC, b"test")
            time.sleep(1)

        producer.close()
