from django.contrib.sites.models import Site, SITE_CACHE

from sites_tools import models


def get_site(request):
    """
    Returns a ``Site`` object for the current host name on request.

    If ``django.contrib.sites`` is not installed, a case insensitive
    ``RequestSite`` will be returned, otherwise the first ``Site`` matching the
    current host name will be returned.

    If no matching ``Site`` object is found, ``None`` is returned.
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
                        pass
        else:
            site = models.CaseInsensitiveRequestSite(request)
        # Save the site object in the cache for faster lookup next time.
        SITE_CACHE[host] = site
    return site
