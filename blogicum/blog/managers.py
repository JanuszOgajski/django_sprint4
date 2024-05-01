from django.db.models import Manager
from django.utils import timezone


class PostManager(Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            pub_date__lt=timezone.now(), is_published=True,
            category__is_published=True)
