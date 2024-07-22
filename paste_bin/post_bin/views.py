import os
import uuid
import logging


from datetime import timedelta, datetime

import boto3
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
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

        paste.hash_value = uuid.uuid4()
        paste.time_expires = datetime.now() + expiration_delta[time_choice]
        paste.content = paste.content[:100]
        paste.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('home')


