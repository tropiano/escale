from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Escale"
admin.site.site_title = "Escale"

urlpatterns = [
    path("admin/", admin.site.urls),
]

# Russian (default) has no prefix: /escapes/…   English: /en/escapes/…
urlpatterns += i18n_patterns(
    path("", include("stays.urls")),
    prefix_default_language=False,
)
