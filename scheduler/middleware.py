"""Module for application middleware"""
from re import compile as comp

from django.http import HttpResponseRedirect
from django.conf import settings

from django.utils.deprecation import MiddlewareMixin


class LoginRequiredMiddleware(MiddlewareMixin):
    """
    Middleware that requires a user to be authenticated to view any page other
    than LOGIN_URL. Exemptions to this requirement can optionally be specified
    in settings via a list of regular expressions in LOGIN_EXEMPT_URLS (which
    you can copy from your urls.py).
    """

    @staticmethod
    def get_exempt_urls():
        """Fetches urls that do not require login"""
        exempt_urls = [comp(settings.LOGIN_URL.lstrip('/'))]
        if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
            exempt_urls += [comp(expr) for expr in settings.LOGIN_EXEMPT_URLS]
        return exempt_urls

    def process_request(self, request):
        """Method checking if user is authenticated"""
        assert hasattr(request, 'user')

        if not request.user.is_authenticated:
            path = request.path_info.lstrip('/')
            if not any(m.match(path) for m in self.get_exempt_urls()):
                return HttpResponseRedirect(settings.LOGIN_URL)
        # required by pylint
        return None
