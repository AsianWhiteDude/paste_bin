import os

import boto3
import redis
from django.contrib.auth import login, authenticate, logout, get_user_model

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User

from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail, EmailMessage
from django.http import HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.cache import cache_page

from django.views.generic import CreateView, UpdateView
from django.core.cache import cache
from post_bin.models import Paste
from .forms import LoginUserForm, SignUpUserLogin, ProfileUserForm, UserPasswordChangeForm
from .tokens import account_activation_token


session = boto3.session.Session()
s3 = session.client(
    service_name='s3',
    endpoint_url='https://storage.yandexcloud.net',
    aws_access_key_id=str(os.getenv('YANDEX_S3_ID_KEY')),
    aws_secret_access_key=str(os.getenv('YANDEX_S3_SECRET_KEY')),
)

redis_client = redis.StrictRedis(host='redis', port=6379, decode_responses=True)

class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'users/login.html'
    extra_context = {'title': 'Pastebin'}

    def get_success_url(self):
        return reverse_lazy('home')


class SignUpUser(CreateView):
    form_class = SignUpUserLogin
    template_name = 'users/sign_up.html'
    extra_context = {'title': 'Pastebin'}

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        current_site = get_current_site(self.request)
        message = render_to_string(
            'users/email.html',
            context={
                "domain": current_site.domain,
                "protocol": "http",
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            }
        )

        send_mail(
            'Подтвердите E-mail',
            message,
            os.environ.get('YANDEX_MAIL'),
            [user.email],
            fail_silently=False,
        )


        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('users:check_email')


def check_email(request):
    return render(request, 'users/check_email.html', context={'title': 'Pastebin'})


class ProfileUser(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = ProfileUserForm
    template_name = 'users/profile.html'
    extra_context = {'title': 'Pastebin'}

    def get_success_url(self):
        return reverse_lazy('users:profile', args=[self.request.user.pk])

    def get_object(self, queryset=None):
        return self.request.user


class PasswordChangeView(PasswordChangeView):
    model = get_user_model()
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy('users:password_change_done')
    template_name = 'users/password_change_form.html'


def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse_lazy('home'))


def verify_email(request, uidb64, token):
    try:
        user_id = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=user_id)
        user.is_active = True
        user.save()

        return render(request, 'users/email_verified.html', context={'title': 'Pastebin'})

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return HttpResponseServerError('<h1>Invalid activation link</h1>')


@cache_page(60 * 2)
def all_posts(request, username):
    user = User.objects.get(username=username)
    posts = Paste.objects.filter(user=user)

    return render(request, 'users/post_history.html',
                  context={'title': 'Pastebin', 'posts': posts, 'username': username})


@cache_page(60 * 2)
def post_details(request, hash):
    post = Paste.objects.get(hash_value=hash)
    posts = Paste.objects.filter(user=request.user.id)

    s3_object = cache.get(post.s3_link)
    if s3_object:
        post.content = s3_object
    else:
        get_object_response = s3.get_object(Bucket='pastebin-app', Key=post.s3_link)
        post.content = get_object_response['Body'].read().decode('utf-8')
        cache.set(post.s3_link, post.content, 60 * 15)

    return render(request, 'users/post_details.html',
                  context={'title': 'Pastebin',
                           'post': post, 'posts': posts, 'user': request.user})