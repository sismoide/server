def easy_post(client, url, data, token):
    return client.post(url, data, format='json', HTTP_AUTHORIZATION="Token {}"
                       .format(token))
