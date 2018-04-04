import pika
import json
from colorama import Fore, Style
from config import RABBITMQ_HOST, RABBITMQ_INPUT_QUEUE_NAME, RABBITMQ_OUTPUT_QUEUE_NAME
from image_processing import ImageProcessor

connection = pika.BlockingConnection(
    pika.ConnectionParameters(RABBITMQ_HOST)
)

channel = connection.channel()
channel.queue_declare(queue=RABBITMQ_INPUT_QUEUE_NAME, durable=True)


# Посылает сообщение в очередь для картинок, ожидаюших конвертации
def send(payload):
    output_connection = pika.BlockingConnection(
        pika.ConnectionParameters(RABBITMQ_HOST)
    )

    output_channel = connection.channel()
    output_channel.queue_declare(queue=RABBITMQ_OUTPUT_QUEUE_NAME, durable=True)

    output_channel.basic_publish(exchange='',
                                 routing_key=RABBITMQ_OUTPUT_QUEUE_NAME,
                                 body=payload)
    print(Fore.GREEN +
          "[Paperclip] Sent data to %r queue" % (RABBITMQ_OUTPUT_QUEUE_NAME, ) +
          Style.RESET_ALL)

    output_connection.close()


# Коллбэк-метод для Rabbit
def callback(ch, method, properties, body):
    # Проверим входящие параметры, распарсим JSON
    try:
        input_data = json.loads(body.decode('utf8'))
        print(Fore.YELLOW +
              "[Paperclip] Received data" +
              Style.RESET_ALL)

        processed_urls = []
        image_id = input_data['data']['id']

        for image_data in input_data['data']['config']:
            processor = ImageProcessor(image_id, image_data)
            processed_urls.append(processor.process_with_s3())

        send(json.dumps(
            {
                'destination': input_data['destination'],
                'data': {
                    'id': image_id,
                    'urls': processed_urls
                }
            }
        ))
    except Exception as e:
        print(Fore.RED +
              '[Paperclip] Failed: ' +
              str(e) +
              Style.RESET_ALL)
        return

    print(Fore.GREEN +
          '[Paperclip] Done' +
          Style.RESET_ALL)

    # Уведомляем Rabbit о том, что мы получили и обработали сообщение
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback, queue=RABBITMQ_INPUT_QUEUE_NAME)

print(Fore.BLUE +
      '[Paperclip] Waiting for messages. To exit press CTRL+C' +
      Style.RESET_ALL)

# Даем Rabbit знать, что мы подписываемся на сообщения с этого канала
channel.start_consuming()
