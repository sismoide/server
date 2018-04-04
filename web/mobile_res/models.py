from django.core.exceptions import ValidationError
from django.db import models


class IntensityQuestion(models.Model):
    """
    question asked to a mobile user when a quiz is triggered,
    after a simple-report is submitted.
    @ text: interrogative text.
    @ position: position in the set of questions that will be asked.
    """
    text = models.TextField(unique=True)  # remove unique if quiz-support is added
    intensity = models.IntegerField(unique=True)

    class Meta:
        ordering = ['intensity']

    def __str__(self):
        return "Intensity {}: {}".format(self.intensity, self.text)


class Coordinates(models.Model):
    """
    latitude and longitude specified in Decimal Degrees (xxx.ddddd)
    elevation specified in Meters above sea.
    """
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
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
    created_on = models.DateTimeField(auto_now=True)
    modified_on = models.DateTimeField(auto_now=True)
    coordinates = models.ForeignKey(Coordinates, on_delete=models.PROTECT)
    intensity = models.IntegerField(blank=True, null=True)
    username = models.TextField()  # todo: auth

    def save(self, *args, **kwargs):
        if self.intensity < 0 or self.intensity > 12:
            raise ValidationError("intensity out of range, given {}".format(self.intensity))
        super().save(*args, **kwargs)


"""
answer model is on-hold as intensity will be calculated on-device, 
then sent to server
"""


# class Answer(models.Model):
#     """
#     user's answer to a question.
#     @ text: answered text
#     @ question: question answered.
#     @ report: user's report related to this answers.
#
#     """
#     text = models.TextField()  # todo: maybe choicefield, check later
#     question = models.ForeignKey(Question, on_delete=models.CASCADE)
#     report = models.ForeignKey(Report, on_delete=models.CASCADE)
#     timestamp = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         unique_together = (('question', 'report'),)
#
#     def __str__(self):
#         return "{} -> {}".format(self.question, self.text)


class Emergency(models.Model):
    """
    type of emergency that can be reported.
    @ title: name of the emergency type
    """
    title = models.TextField(unique=True)


class Threat(models.Model):
    """
    type of threat that can be reported.
    @ title: name of the threat type

    """
    title = models.TextField(unique=True)


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
    type = models.ForeignKey(Emergency, on_delete=models.CASCADE)


class ThreatReport(EventReport):
    """
    threat report submitted by mobile user.

    """
    type = models.ForeignKey(Threat, on_delete=models.CASCADE)
