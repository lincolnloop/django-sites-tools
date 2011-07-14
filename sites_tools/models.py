from django.contrib.sites.models import RequestSite


class CaseInsensitiveRequestSite(RequestSite):
    """
    A subclass of django.contrib.sites.models.RequestSite
    which uses a case insensitive host name.
    """
    def __init__(self, request):
        self.domain = self.name = request.get_host().lower()
