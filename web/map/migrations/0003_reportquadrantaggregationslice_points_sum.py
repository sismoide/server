# Generated by Django 2.0.2 on 2018-06-18 16:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('map', '0002_auto_20180601_2138'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportquadrantaggregationslice',
            name='points_sum',
            field=models.IntegerField(default=0),
        ),
    ]
