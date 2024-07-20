from django import forms
from django.contrib.auth import get_user_model
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3

from post_bin.models import Paste


class PastePost(forms.ModelForm):
    TIME_CHOICES = (
        ('1day', '1 День'),
        ('1week', '1 Неделя'),
        ('1month', '1 Месяц'),
        ('3months', '3 Месяца'),
        ('6months', '6 Месяцев'),
    )


    title = forms.CharField(label='Название', required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control',
                                                             'id': 'UsernameForm',
                                                             'placeholder': 'Введите название'}))

    time_expire = forms.ChoiceField(label='Время Истечения Ссылки',
                                    choices=TIME_CHOICES,
                                    widget=forms.Select(attrs={'class': 'form-control'}),
                                    initial='6months')

    content = forms.CharField(label='Содержимое',
                              widget=forms.Textarea(attrs={
                                    'class': 'form-control',
                                    'id': 'PasswordField',
                                    'placeholder': 'Введите содержимое'
                                }))

    captcha = ReCaptchaField(label='', widget=ReCaptchaV3())


    def clean_content(self):
        content = self.cleaned_data.get('content')
        if content:
            content_length = len(content.encode('utf-8'))
            if content_length > 10 * 1024 * 1024:  # 10 MB in bytes
                raise forms.ValidationError('Размер файла не должен превышать 10 MB.')
        return content


    class Meta:
        model = Paste
        fields = ['title', 'time_expire', 'content']

