from django.conf import settings
from django.db import models
from django.db.models.fields import FieldDoesNotExist


class SiteAwareManager(models.Manager):
    """
    Use this to limit objects to those associated with a site.

    Usage::
    
        on_site = SiteAwareManager()
        on_site = SiteAwareManager("package__site")
        on_site = SiteAwareManager("release__package__site")
        on_site = SiteAwareManager("release__package__site", select_related=False)

    """
    def __init__(self, field_name=None, select_related=False, *args, **kwargs):
        self.__field_name = field_name
        self.__select_related = select_related
        super(SiteAwareManager, self).__init__(*args, **kwargs)

    @property
    def site_field_name(self):
        if self.__field_name:
            return self.__field_name
        potential_names = ('site', 'sites')
        for potential_name in potential_names:
            try:
                field = self.model._meta.get_field(potential_name)
                if isinstance(field, (models.ForeignKey,
                                      models.ManyToManyField)):
                    self.__field_name = potential_name
                    return potential_name
            except FieldDoesNotExist:
                pass
        raise ValueError("%s couldn't find a related field named %s in %s." %
                (self.__class__.__name__, ' or '.join(potential_names),
                 self.model._meta.object_name))

    def get_query_set(self):
        return super(SiteAwareManager, self).get_query_set()

    def by_id(self, site_id=None):
        if site_id is None:
            site_id = settings.SITE_ID
        qs = self.filter(**{self.site_field_name + '__id__exact': site_id})
        if self.__select_related:
            qs = qs.select_related(depth=1)
        return qs

    def by_request(self, request):
        # Using an equality check here because Django 1.3 doesn't do a good
        # enough job of SimpleLazyObject to do a basic boolean check.
        if getattr(request, 'site', None) == None:
            return self.none()
        return self.by_id(request.site.pk)
