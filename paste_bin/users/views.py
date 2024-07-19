import os

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

from django.views.generic import CreateView, UpdateView


from .forms import LoginUserForm, SignUpUserLogin, ProfileUserForm, UserPasswordChangeForm
from .tokens import account_activation_token


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'users/login.html'
    extra_context = {'title': 'Взял Да Вставил!'}

    def get_success_url(self):
        return reverse_lazy('home')


class SignUpUser(CreateView):
    form_class = SignUpUserLogin
    template_name = 'users/sign_up.html'
    extra_context = {'title': 'Взял Да Вставил!'}

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
    return render(request, 'users/check_email.html', context={'title': 'Blog Generator'})


class ProfileUser(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = ProfileUserForm
    template_name = 'users/profile.html'
    extra_context = {'title': 'Взял Да Вставил!'}

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

        return render(request, 'users/email_verified.html', context={'title': 'Взял Да Вставил!'})

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return HttpResponseServerError('<h1>Invalid activation link</h1>')