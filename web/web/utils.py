from threading import Thread


def easy_post(client, url, data, token):
    return client.post(url, data, format='json', HTTP_AUTHORIZATION="Token {}"
                       .format(token))


def easy_get(client, url, data, token):
    return client.get(url, data, HTTP_AUTHORIZATION="Token {}".format(token))


def async(fun):
    """
    Defines a decorator for asynchronous functions.
    :param fun:
    :return:
    """

    def decorator(*args, **kwargs):
        t = Thread(target=fun, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()

    return decorator
