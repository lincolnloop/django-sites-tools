from django.conf import settings
from django.contrib.sites.models import Site, SITE_CACHE

from sites_tools import models


def get_site(request):
    """
    Returns a ``Site`` object for the current host name on request.

    If ``django.contrib.sites`` is not installed, a case insensitive
    ``RequestSite`` will be returned, otherwise the first ``Site`` matching the
    current host name will be returned.

    If no matching ``Site`` object is found, the default behaviour is to return
    ``None``. This can be altered via the ``SITES_FALLBACK`` Django setting:
    
    * Set to ``'default'`` to return the default site as defined by
      ``SITE_ID``, or

    * set to ``'request'`` to return a case insensitive ``RequestSite``.
    """
    host = request.get_host().lower()
    # Try to retrieve the site object from cache.
    site = SITE_CACHE.get(host, None)
    if site is None:
        if Site._meta.installed:
            # Look for a site matching the full host name.
            matches = Site.objects.filter(domain__iexact=host)
            try:
                site = matches[0]
            except IndexError:
                # If no match was found and the host name contained a port, try
                # looking again for a site matching just the domain.
                if ':' in host:
                    domain = host.split(':', 1)[0]
                    matches = Site.objects.filter(domain__iexact=domain)
                    try:
                        site = matches[0]
                    except IndexError:
                        fallback = getattr(settings, 'SITES_FALLBACK', None)
                        if fallback == 'default':
                            site = Site.objects.get_current()
                        elif fallback == 'request':
                            site = models.CaseInsensitiveRequestSite(request)
        else:
            site = models.CaseInsensitiveRequestSite(request)
        # Save the site object in the cache for faster lookup next time.
        SITE_CACHE[host] = site
    return site
