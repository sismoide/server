from django.core.management import BaseCommand

from mobile_res.models import MobileUser


class Command(BaseCommand):
    def handle(self, *args, **options):
        wu = MobileUser.objects.create_random_mobile_user()

        print("\n\nMobile User created successfully.\n")
        if input("Press enter to print token. Ctrl+C to leave."):
            return
        print("{}".format(wu.token))
