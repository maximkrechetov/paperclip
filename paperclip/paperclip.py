import logging

from colorama import Fore, Style
from consumer import Consumer


def main():
    print(Fore.BLUE +
          '[Paperclip] Waiting for messages. To exit press CTRL+C' +
          Style.RESET_ALL)

    consumer = Consumer()
    consumer.process()

if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s.%(msecs)s:%(name)s:%(thread)d:%(levelname)s:%(process)d:%(message)s',
        level=logging.INFO
    )
    main()
