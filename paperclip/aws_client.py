import boto3
from config import AWS

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
