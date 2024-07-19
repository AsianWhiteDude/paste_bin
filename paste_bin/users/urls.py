from django.contrib.auth.views import PasswordResetDoneView, PasswordResetView, PasswordResetConfirmView, \
    PasswordResetCompleteView, PasswordChangeView, PasswordChangeDoneView
from django.urls import path, reverse_lazy
from . import views

app_name = 'reviews'

urlpatterns = [
    path('login/', views.LoginUser.as_view(), name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('sign_up/', views.SignUpUser.as_view(), name='sign_up'),
    path('verify_email/<uidb64>/<str:token>/', views.verify_email, name='verify_email'),
    path('check_email/', views.check_email, name='check_email'),
    path('password-reset/',
         PasswordResetView.as_view(template_name='users/password_reset_form.html',
                                   email_template_name='users/password_reset_email.html',
                                   success_url=reverse_lazy('users:password_reset_done')),
         name='password_reset'),
    path('password-reset/done/',
         PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html',
                                          success_url=reverse_lazy('users:password_reset_complete')),
         name='password_reset_confirm'),
    path('password-reset/complete/',
         PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),
    path('password-change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('password-change/done/', PasswordChangeDoneView.as_view(template_name='users/password_change_done.html'),
         name='password_change_done'),
    path('profile/', views.ProfileUser.as_view(), name='profile'),
]