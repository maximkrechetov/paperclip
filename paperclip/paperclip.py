import pika
import json
from colorama import Fore, Style
from multiprocessing import Pool
from config import RABBITMQ_HOST, RABBITMQ_INPUT_QUEUE_NAME, RABBITMQ_OUTPUT_QUEUE_NAME,\
    RABBITMQ_LOGIN, RABBITMQ_PASSWORD, POOL_PROCESSES
from image_processing import ImageProcessor

credentials = pika.PlainCredentials(RABBITMQ_LOGIN, RABBITMQ_PASSWORD)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(RABBITMQ_HOST, credentials=credentials)
)

channel = connection.channel()
channel.queue_declare(queue=RABBITMQ_INPUT_QUEUE_NAME, durable=True)


# Посылает сообщение в очередь для картинок, ожидаюших конвертации
def _send(payload):
    output_connection = pika.BlockingConnection(
        pika.ConnectionParameters(RABBITMQ_HOST, credentials=credentials)
    )

    output_channel = connection.channel()
    output_channel.queue_declare(queue=RABBITMQ_OUTPUT_QUEUE_NAME, durable=True)

    output_channel.basic_publish(exchange='',
                                 routing_key=RABBITMQ_OUTPUT_QUEUE_NAME,
                                 body=json.dumps(payload))
    print(Fore.YELLOW +
          "[Paperclip] Sent data to %r queue" % (RABBITMQ_OUTPUT_QUEUE_NAME, ) +
          Style.RESET_ALL)

    output_connection.close()


# Метод для передачи в pool.map для распараллеливания
def _process_image(image_config):
    return ImageProcessor(image_config).process_with_s3()


# Коллбэк-метод для Rabbit
def callback(ch, method, properties, body):
    print(Fore.YELLOW +
          "[Paperclip] Received data" +
          Style.RESET_ALL)

    print(Fore.YELLOW +
          "[Paperclip] " +
          str(body) +
          Style.RESET_ALL)

    # Уведомляем Rabbit о том, что мы получили и обработали сообщение
    ch.basic_ack(delivery_tag=method.delivery_tag)

    try:
        input_data = json.loads(body.decode('utf8'))
        image_id = input_data['data']['id']
    except:
        _send({
                'ok': False,
                'error': 'Failed to parse input data. Data may be incorrect.'
            })
        return

    # Проверим входящие параметры, распарсим JSON
    try:
        pool = Pool(processes=POOL_PROCESSES)
        processed_urls = pool.map(_process_image, input_data['data']['config'])
        pool.close()
        pool.join()
        print(Fore.GREEN +
              '[Paperclip] Successfully done' +
              Style.RESET_ALL)

        _send({
                'ok': True,
                'destination': input_data['destination'],
                'data': {
                    'id': image_id,
                    'urls': processed_urls
                }
            })
    except Exception as e:
        _send({
                'ok': False,
                'error': 'Failed to convert images: {}'.format(e)
            })

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback, queue=RABBITMQ_INPUT_QUEUE_NAME)

print(Fore.BLUE +
      '[Paperclip] Waiting for messages. To exit press CTRL+C' +
      Style.RESET_ALL)

# Даем Rabbit знать, что мы подписываемся на сообщения с этого канала
channel.start_consuming()
