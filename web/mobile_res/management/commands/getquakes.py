from django.core.management import BaseCommand

from mobile_res.urls import check_quakes


class Command(BaseCommand):

    def handle(self, *args, **options):
        check_quakes()
