Приложение работает на Python 3.x (>= 3.5).

Сборка и запуск в docker:

sudo docker-compose Docker
sudo docker-compose up

Сборка и запуск локально без Docker:

Для запуска должны быть установлены Python 3.x, python3-pip.

Устанавливаем пакеты:
cd /%папка_с_проектами/paperclip
pip install -r requirements.txt

Настраиваем приложение с помощью .env файла. Пример показан в .env.sample

Запуск:
python paperclip/paperclip.py