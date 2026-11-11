from django.urls import translate_url
from django.utils.translation import get_language

from .models import Destination


def site(request):
    path = request.get_full_path()
    return {
        "nav_destinations": Destination.objects.all(),
        "site_name": "Escale",
        "lang": get_language(),
        # Same page in the other language, for the RU / EN switcher and hreflang tags.
        "lang_urls": {"ru": translate_url(path, "ru"), "en": translate_url(path, "en")},
    }
