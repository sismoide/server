from django.core.exceptions import ValidationError
from django.db import models


# class Quiz(models.Model):
#     """
#     set of questions asked to a mobile user when a simple-report is submitted
#     """
#     title = models.TextField()


class Question(models.Model):
    """
    question asked to a mobile user when a quiz is triggered,
    after a simple-report is submitted.
    @ text: interrogative text.
    @ position: position in the set of questions that will be asked.
    """
    text = models.TextField(unique=True)  # remove unique if quiz-support is added
    position = models.IntegerField(unique=True)

    # quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)

    class Meta:
        ordering = ['position']

    def __str__(self):
        return "{}: {}".format(self.position, self.text)


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
    @ timestamp: time when report was submitted.
    @ coordinates: where the report wes submitted.
    @ intensity: Mercalli's intensity recorded by user.

    """
    timestamp = models.DateTimeField(auto_now=True)
    coordinates = models.ForeignKey(Coordinates, on_delete=models.PROTECT)
    intensity = models.IntegerField(blank=True, null=True)
    username = models.TextField()  # todo: auth

    def save(self, *args, **kwargs):
        if self.intensity < 0 or self.intensity > 12:
            raise ValidationError("intensity out of range, given {}".format(self.intensity))
        super().save(*args, **kwargs)


class Answer(models.Model):
    """
    user's answer to a question.
    @ text: answered text
    @ question: question answered.
    @ report: user's report related to this answers.

    """
    text = models.TextField()  # todo: maybe choicefield, check later
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('question', 'report'),)

    def __str__(self):
        return "{} -> {}".format(self.question, self.text)
