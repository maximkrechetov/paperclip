import boto3
import os
from config import AWS, TMP_DIR

s3 = boto3.client(
    's3',
    endpoint_url=AWS['endpoint_url'],
    aws_access_key_id=AWS['access_key'],
    aws_secret_access_key=AWS['secret_key']
)

# Создание области памяти для оригиналов картинок, если еще не существует
s3.create_bucket(Bucket=AWS['original_files_bucket_name'])

# Создание области памяти для обработанных картинок, если еще не существует
s3.create_bucket(Bucket=AWS['processed_files_bucket_name'])

# Создать папку в /tmp/, если ее еще нет
if not os.path.exists(TMP_DIR):
    os.makedirs(TMP_DIR)
