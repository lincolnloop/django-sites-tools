from django.conf import settings
from django.utils.cache import patch_vary_headers
from django.utils.functional import SimpleLazyObject

from sites_tools import utils


def get_site(request, obj_type=None):
    if not hasattr(request, '_cached_site'):
        request._cached_site = utils.get_site(request)
    return request._cached_site


class SitesMiddleware(object):

    def process_request(self, request):
        request.site = SimpleLazyObject(lambda: get_site(request))

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
