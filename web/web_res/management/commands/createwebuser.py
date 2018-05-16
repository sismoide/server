from django.contrib.auth.models import User
from django.core.management import BaseCommand

from mobile_res.utils import random_username
from web_res.models import WebUser


def get_password():
    password = input("enter password (leave blank for random)")
    if password is None or password == "":
        password = User.objects.make_random_password()
    if len(password) < 8:
        print("password need 8+ length")
        return get_password()
    return password


def get_username():
    username = input("enter username (leave blank for random)")
    if username is None or username == "":
        username = random_username()
    return username


def get_email():
    email = input("enter email (leave blank for set None address)")
    return email


class Command(BaseCommand):
    def handle(self, *args, **options):
        username = get_username()
        password = get_password()
        email = get_email()

        wu = WebUser.objects.create_web_user(
            username,
            email,
            password
        )

        print("\n\nWeb User created successfully.\n")
        print("Created user Credentials:\n Username:{}\n Email:{}\n".format(username, email))
        if input("Press enter to print token. Ctrl+C to leave."):
            return
        print("{}".format(wu.token))
        if input("Press enter to print plain password. Ctrl+C to leave."):
            return
        print("{}".format(password))
