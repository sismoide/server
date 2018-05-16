import uuid


def random_username():
    return str(uuid.uuid5(uuid.uuid4(), "django:user"))[:11]
