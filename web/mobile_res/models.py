
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class IntensityQuestion(models.Model):
    """
    question asked to a mobile user when a quiz is triggered,
    after a simple-report is submitted.
    @ text: interrogative text.
    @ intensity: intensity that this question represent.
    """
    text = models.TextField(unique=True)  # remove unique if quiz-support is added
    intensity = models.IntegerField(unique=True)

    class Meta:
        ordering = ['intensity']

    def save(self, *args, **kwargs):
        if self.intensity < 0 or self.intensity > 12:
            raise ValidationError("intensity out of range, given {}".format(self.intensity))
        super().save(*args, **kwargs)

    def __str__(self):
        return "Intensity {}: {}".format(self.intensity, self.text)


class Coordinates(models.Model):
    """
    latitude and longitude specified in Decimal Degrees (xxx.ddddddddd)
    elevation specified in Meters above sea.
    """
    latitude = models.DecimalField(max_digits=13, decimal_places=10)
    longitude = models.DecimalField(max_digits=13, decimal_places=10)
    elevation = models.FloatField(blank=True, null=True)

    def __str__(self):
        return "{}, {} [{} m]".format(self.latitude, self.longitude, self.elevation) if self.elevation else "{}, {}".format(self.latitude, self.longitude)


class Report(models.Model):
    """
    report submitted by a mobile app user.
    @ created_on: time when report instance was submitted.
    @ modified_on: time when report instance was modified.
    @ coordinates: where the report wes submitted.
    @ intensity: Mercalli's intensity recorded by user.

    """
    created_on = models.DateTimeField(editable=False, default=timezone.now())
    modified_on = models.DateTimeField(default=timezone.now())
    coordinates = models.ForeignKey(Coordinates, on_delete=models.PROTECT)
    intensity = models.IntegerField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.modified_on = timezone.now()

        # at any case cehck constraint
        if self.intensity:
            if self.intensity < 0 or self.intensity > 12:
                raise ValidationError("intensity out of range, given {}".format(self.intensity))
        # update modified datetime
        super().save(*args, **kwargs)

    def __str__(self):
        return "id:{} in ({}) on {}".format(self.id, self.coordinates, self.created_on)


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
