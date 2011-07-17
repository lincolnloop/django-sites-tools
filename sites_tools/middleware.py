from django.conf import settings
from django.utils.cache import patch_vary_headers

from sites_tools import utils


class LazySite(object):
    """
    A lazy site object that refers to either Site instance or
    a case insensitive RequestSite.
    """

    def __get__(self, request, obj_type=None):
        if not hasattr(request, '_cached_site'):
            request._cached_site = utils.get_site(request)
        return request._cached_site


class SitesMiddleware(object):

    def process_request(self, request):
        if not hasattr(request.__class__, 'site'):
            request.__class__.site = LazySite()

    def process_response(self, request, response):
        """
        Forces the HTTP Vary header onto requests to avoid having responses
        cached from incorrect urlconfs.

        If you'd like to disable this for some reason, set `FORCE_VARY_ON_HOST`
        in your Django settings file to `False`.
        """
        if getattr(settings, 'SITES_VARY_ON_HOST', True):
            patch_vary_headers(response, ('Host',))
        return response
