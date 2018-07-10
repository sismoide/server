from __future__ import unicode_literals

from django.utils.six import text_type
from django.utils.translation import ugettext_lazy as _
from rest_framework import HTTP_HEADER_ENCODING, exceptions

from mobile_res.models import MobileUser
from web.settings import MOBILE_PATH_PREFIX, MAP_PATH_PREFIX
from web_res.models import WebUser


def get_authorization_header(request):
    """
    Return request's 'Authorization:' header, as a bytestring.

    Hide some test client ickyness where the header can be unicode.
    """
    auth = request.META.get('HTTP_AUTHORIZATION', b'')
    if isinstance(auth, text_type):
        # Work around django test client oddness
        auth = auth.encode(HTTP_HEADER_ENCODING)
    return auth


class BaseAuthentication(object):
    """
    All authentication classes should extend BaseAuthentication.
    """

    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token).
        """
        raise NotImplementedError(".authenticate() must be overridden.")

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        pass


class TokenAuthentication(BaseAuthentication):
    """
    Simple token based authentication.

    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "Token ".  For example:

        Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a
    """

    keyword = 'Token'
    model = None
    request = None

    def get_model(self):
        if self.model is not None:
            return self.model
        from rest_framework.authtoken.models import Token
        return Token

    """
    A custom token model may be used, but must have the following properties.

    * key -- The string identifying the token
    * user -- The user to which the token belongs
    """

    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        self.request = request

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = _('Invalid token header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid token header. Token string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = _('Invalid token header. Token string should not contain invalid characters.')
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        # check if user is mobile or web
        is_mobile, is_web = False, False
        try:
            MobileUser.objects.get(token=token)
            is_mobile = True
        except MobileUser.DoesNotExist:
            pass
        try:
            WebUser.objects.get(token=token)
            is_web = True
        except WebUser.DoesNotExist:
            pass

        if not is_mobile and not is_web:
            if not token.user.is_superuser:
                raise exceptions.AuthenticationFailed(_('User not mobile neither web.'))

        if is_mobile:
            if MOBILE_PATH_PREFIX not in self.request.path and MAP_PATH_PREFIX not in self.request.path:
                raise exceptions.AuthenticationFailed(_('Mobile user is restricted to mobile and map resources.'))
        return token.user, token

    def authenticate_header(self, request):
        return self.keyword
