import datetime
import os

import boto3
from celery import Celery
from celery.schedules import crontab
from sqlalchemy import select, delete

from database.engine import Session
from database.models import Paste

celery = Celery(
    'cleaner',
    backend='redis://redis:6379/1',
    broker='redis://redis:6379/1',
)

celery.conf.beat_schedule = {
    'run-every-midnight': {
        'task': 'cleaner.clean_database',
        'schedule': 60.0 * 60,
    },
}

session = boto3.session.Session()
s3 = session.client(
    service_name='s3',
    endpoint_url='https://storage.yandexcloud.net',
    aws_access_key_id=str(os.getenv('YANDEX_S3_ID_KEY')),
    aws_secret_access_key=str(os.getenv('YANDEX_S3_SECRET_KEY')),
)

@celery.task()
def clean_database():

    session = Session()

    query = session.execute(statement=select(Paste).where(Paste.time_expires < datetime.datetime.now(datetime.UTC)))
    expired_pastes = query.scalars().all()

    for paste in expired_pastes:
        s3.delete_object(Bucket='pastebin-app', Key=paste.s3_link)

    session.execute(statement=delete(Paste).where(Paste.time_expires < datetime.datetime.now(datetime.UTC)))
    session.commit()
    session.close()
    return 'EXECUTED'

