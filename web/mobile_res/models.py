from django.core.exceptions import ValidationError
from django.db import models


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
    """
    timestamp = models.DateTimeField(auto_now=True)
    coordinates = models.ForeignKey(Coordinates, on_delete=models.PROTECT)
    intensity = models.IntegerField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.intensity < 0 or self.intensity > 12:
            raise ValidationError("intensity out of range, given {}".format(self.intensity))
        super().save(*args, **kwargs)



