from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
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
    token = models.OneToOneField(Token, null=True, blank=True, on_delete=models.SET_NULL)
    objects = WebUserManager()

    def save(self, *args, **kwargs):
        if self.token is "" or self.token is None:
            self.token = Token.objects.get_or_create(user=self.user)[0]
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.user)


@receiver(pre_save, sender=User)
def reset_token(sender, instance, **kwargs):
    """
    Any time a Django User data is modified, a new token is generated.
    :param sender:
    :param instance:
    :param kwargs:
    :return: None
    """
    try:
        # try to get web_user of django_user
        web_user = WebUser.objects.get(user=instance)
        if web_user.token:
            # delete old token
            web_user.token.delete()
            # generate new one
            web_user.token = Token.objects.get_or_create(user=instance)[0]
            web_user.save()
    except WebUser.DoesNotExist:
        pass
