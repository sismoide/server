from django.contrib.auth.models import User
from django.db import models
from rest_framework.authtoken.models import Token


class WebUserManager(models.Manager):

    def create_web_user(self, name, email=None, password=None):
        django_user = User.objects.create_user(name, email, password)
        web_user = WebUser.objects.create(user=django_user)
        return web_user


class WebUser(models.Model):
    """
    Django's user has:
        username
        password
        email
        first_name
        last_name
    Django's user is created by:
        User.objects.create_user(name, email, plain_pass)
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.TextField(blank=True)
    objects = WebUserManager()

    def save(self, *args, **kwargs):
        if self.token is "" or self.token is None:
            self.token = Token.objects.get_or_create(user=self.user)[0]
        super().save(*args, **kwargs)
