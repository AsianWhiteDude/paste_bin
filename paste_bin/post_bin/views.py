import os
import uuid
import requests

from typing import TYPE_CHECKING
import logging

from datetime import timedelta, datetime

import boto3
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView, CreateView
from post_bin.forms import PastePost
from post_bin.models import Paste


logger = logging.getLogger(__name__)
logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
                '[%(asctime)s] - %(name)s - %(message)s')


session = boto3.session.Session()
s3 = session.client(
    service_name='s3',
    endpoint_url='https://storage.yandexcloud.net',
    aws_access_key_id=str(os.getenv('YANDEX_S3_ID_KEY')),
    aws_secret_access_key=str(os.getenv('YANDEX_S3_SECRET_KEY')),
)

flask_app_url = 'http://flask:5000/get_hash_key'




from .rmq_config import (
    get_connection,
    configure_logging,
    MQ_ROUTING_KEY,
)


if TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingChannel
    from pika.spec import Basic, BasicProperties



def process_new_message(
        ch: "BlockingChannel",
        method: "Basic.Deliver",
        properties: "BasicProperties",
        body,
):

    logger.info("Finished processing message %r, sending ack!", body)

    ch.basic_ack(delivery_tag=method.delivery_tag)



def consume_one_message(channel: "BlockingChannel") -> None:
    method_frame, header_frame, body = channel.basic_get(queue=MQ_ROUTING_KEY, auto_ack=False)

    if method_frame:
        process_new_message(channel, method_frame, header_frame, body)
        return body
    else:
        logger.warning("No message returned.")


def get_hash():

    response = requests.get(flask_app_url)

    configure_logging(level=logging.WARNING)
    with get_connection() as connection:
        logger.info("Created connection: %s", connection)
        with connection.channel() as channel:
            logger.info("Created channel: %s", channel)
            hash_key = consume_one_message(channel=channel)

    hash_key = hash_key.decode('utf-8')

    return hash_key




def generate_random_string():
    random_string = str(uuid.uuid4())
    return random_string

class Index(LoginRequiredMixin, CreateView):
    model = Paste
    form_class = PastePost
    template_name = 'post_bin/index.html'

    user = get_user_model()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = Paste.objects.filter(user=self.request.user)[:10]
        context['title'] = 'Pastebin'
        context['user'] = self.request.user
        return context

    def form_valid(self, form):

        paste = form.save(commit=False)
        paste.user = self.request.user


        unique_id = generate_random_string()
        file_name = f"content_{unique_id}.txt"

        s3.put_object(Bucket='pastebin-app', Key=file_name, Body=paste.content)

        paste.s3_link = file_name

        time_choice = form.cleaned_data['time_expire']
        expiration_delta = {
            '1day': timedelta(days=1),
            '1week': timedelta(days=7),
            '1month': timedelta(days=30),
            '3months': timedelta(days=90),
            '6months': timedelta(days=180),
        }

        paste.hash_value = get_hash()

        paste.time_expires = datetime.now() + expiration_delta[time_choice]
        paste.content = paste.content[:100]
        paste.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('home')


