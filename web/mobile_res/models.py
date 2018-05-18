import datetime
import uuid

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from rest_framework.authtoken.models import Token

from mobile_res.utils import random_username
from map.models import Coordinates
from web.settings import NONCE_EXPIRATION_TIME, HASH_CLASS


class MobileUserManager(models.Manager):
    def create_random_mobile_user(self):
        # generate random user & password
        django_user = User.objects.create_user(random_username())
        django_user.set_password(User.objects.make_random_password())
        django_user.save()
        return MobileUser.objects.create(user=django_user)


class Report(models.Model):
    """
    report submitted by a mobile app user, read by web user.
    @ created_on: time when report instance was submitted.
    @ modified_on: time when report instance was modified.
    @ coordinates: where the report wes submitted.
    @ intensity: Mercalli's intensity recorded by user.

    """
    created_on = models.DateTimeField(editable=False, default=timezone.now())
    modified_on = models.DateTimeField(default=timezone.now())
    coordinates = models.ForeignKey('map.Coordinates', on_delete=models.PROTECT)
    intensity = models.IntegerField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # at any case cehck constraint
        if self.intensity:
            if self.intensity < 0 or self.intensity > 12:
                raise ValidationError("intensity out of range, given {}".format(self.intensity))
        # update modified datetime
        self.modified_on = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return "id:{} in ({}) on {}".format(self.id, self.coordinates, self.created_on)


class MobileUser(models.Model):
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
    objects = MobileUserManager()

    def save(self, *args, **kwargs):
        if self.token is "" or self.token is None:
            self.token = Token.objects.get_or_create(user=self.user)[0]
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.user)


class EventType(models.Model):
    title = models.TextField(unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


class EmergencyType(EventType):
    """
    type of emergency that can be reported.
    @ title: name of the emergency type
    """


class ThreatType(EventType):
    """
    type of threat that can be reported.
    @ title: name of the threat type
    """


class EventReport(models.Model):
    """
    abstract model for any event report that can be attached to the user's report
    """
    # have to be define a Type of event
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('type', 'report'),)
        abstract = True


class EmergencyReport(EventReport):
    """
    emergency report submitted by mobile user.
    """
    type = models.ForeignKey(EmergencyType, on_delete=models.CASCADE)


class ThreatReport(EventReport):
    """
    threat report submitted by mobile user.

    """
    type = models.ForeignKey(ThreatType, on_delete=models.CASCADE)


class Quake(models.Model):

    eventid = models.CharField(primary_key=True, max_length=14)
    coordinates = models.ForeignKey(Coordinates, on_delete=models.PROTECT)
    depth = models.FloatField(default=0)
    magnitude = models.FloatField(default=0)
    timestamp = models.DateTimeField(default=timezone.now())
    creation_time = models.DateTimeField(default=timezone.now())

    def save(self, *args, **kwargs):
        if self.depth:
            if self.depth < 0:
                raise ValidationError("Negative depth ({} m) not allowed.".format(self.depth))

        if self.magnitude:
            if self.magnitude < 0:
                raise ValidationError("Negative magnitude ({}) not allowed".format(self.magnitude))

        super().save(*args, **kwargs)

    def __str__(self):
        return "{}: {} quake at {}".format(self.eventid, self.magnitude, self.timestamp)


# Auth

def clean_expired_nonces():
    timeout_limit_time = timezone.now() - datetime.timedelta(seconds=NONCE_EXPIRATION_TIME)
    n = Nonce.objects.filter(created_on__lt=timeout_limit_time)
    n.delete()


class Nonce(models.Model):
    """
    Cryptographic Nonce
    """
    key = models.TextField(null=True, blank=True)
    expected_response = models.TextField(null=True, blank=True)
    created_on = models.DateTimeField(null=True, blank=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        clean_expired_nonces()  # maybe is too demanding
        if not self.pk:
            self.key = uuid.uuid1().hex + uuid.uuid4().hex
            self.created_on = timezone.now()
            # calculate hash of key + secret (None by now)
            self.expected_response = HASH_CLASS(self.key.encode('utf-8')).hexdigest()
        super().save(force_insert, force_update, using, update_fields)
