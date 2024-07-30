from django.contrib.auth.models import User
from django.db import models


class Paste(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, null=False)
    content = models.TextField()
    s3_link = models.URLField()
    hash_value = models.CharField(max_length=255, unique=True)
    time_create = models.DateTimeField(auto_now_add=True)
    time_expires = models.DateTimeField()

