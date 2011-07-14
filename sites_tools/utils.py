from django.contrib.sites.models import Site, RequestSite, SITE_CACHE

from sites_tools import models


def get_site(request):
    """
    
    Returns either a Site instance or a case insensitive RequestSite.
    """
    host = request.get_host().lower()
    if ':' in host:
        host = host.split(':', 1)[0]
    # First check, if there are any cached sites
    site = SITE_CACHE.get(host, None)
    if site is None:
        if Site._meta.installed:
            # Secondly, find the matching Site objects and set the cache
            matches = Site.objects.filter(domain__iexact=host)
            try:
                site = matches[0]
            except IndexError:
                site = None
        else:
            site = models.CaseInsensitiveRequestSite(request)
        SITE_CACHE[host] = site
    return site
