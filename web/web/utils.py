def easy_post(client, url, data, token):
    return client.post(url, data, format='json', HTTP_AUTHORIZATION="Token {}"
                       .format(token))


def easy_get(client, url, data, token):
    return client.get(url, data, HTTP_AUTHORIZATION="Token {}".format(token))
