from django.db import models
from django.urls import reverse
from django.utils import timezone, translation
from django.utils.translation import gettext_lazy as _


class _Translated:
    """Template helper: `obj.t.title` returns `title_en` when the page is in English
    (falling back to the Russian `title` if the English one is empty)."""

    def __init__(self, obj):
        self._obj = obj

    def __getattr__(self, name):
        if translation.get_language() == "en":
            value = getattr(self._obj, f"{name}_en", "")
            if value:
                return value
        return getattr(self._obj, name)


class Translatable(models.Model):
    class Meta:
        abstract = True

    @property
    def t(self):
        return _Translated(self)


class Destination(Translatable):
    name = models.CharField(_("name (RU)"), max_length=80)
    name_en = models.CharField(_("name (EN)"), max_length=80, blank=True)
    slug = models.SlugField(unique=True)
    tagline = models.CharField(_("tagline (RU)"), max_length=160, blank=True)
    tagline_en = models.CharField(_("tagline (EN)"), max_length=160, blank=True)
    image_url = models.URLField(max_length=500)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("stays:destination", args=[self.slug])


class Escape(Translatable):
    """A curated hotel offer: one members-only sale for a city weekend."""

    class Mood(models.TextChoices):
        ROMANTIC = "romantic", _("For two")
        FRIENDS = "friends", _("With friends")
        SPA = "spa", _("Spa & wellness")
        GASTRONOMY = "gastronomy", _("Gastronomy")

    slug = models.SlugField(unique=True)
    hotel_name = models.CharField(_("hotel name (RU)"), max_length=120)
    hotel_name_en = models.CharField(_("hotel name (EN)"), max_length=120, blank=True)
    title = models.CharField(_("headline (RU)"), max_length=140)
    title_en = models.CharField(_("headline (EN)"), max_length=140, blank=True)
    destination = models.ForeignKey(Destination, on_delete=models.PROTECT, related_name="escapes")
    neighbourhood = models.CharField(_("neighbourhood (RU)"), max_length=80, blank=True)
    neighbourhood_en = models.CharField(_("neighbourhood (EN)"), max_length=80, blank=True)
    stars = models.PositiveSmallIntegerField(default=5)
    mood = models.CharField(max_length=20, choices=Mood.choices, default=Mood.ROMANTIC)
    summary = models.CharField(_("summary (RU)"), max_length=240)
    summary_en = models.CharField(_("summary (EN)"), max_length=240, blank=True)
    description = models.TextField(_("description (RU)"))
    description_en = models.TextField(_("description (EN)"), blank=True)
    inclusions = models.TextField(_("inclusions (RU)"), help_text=_("One perk per line"))
    inclusions_en = models.TextField(_("inclusions (EN)"), blank=True, help_text=_("One perk per line"))
    image_url = models.URLField(max_length=500)
    gallery = models.TextField(blank=True, help_text=_("One image URL per line"))
    price = models.PositiveIntegerField(_("member price, ₽ per night for two"))
    original_price = models.PositiveIntegerField(_("public price, ₽ per night"))
    min_nights = models.PositiveSmallIntegerField(default=1)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=9.0)
    ends_at = models.DateTimeField(_("sale closes at"))
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_featured", "ends_at"]

    def __str__(self):
        return f"{self.hotel_name} — {self.destination}"

    def get_absolute_url(self):
        return reverse("stays:escape", args=[self.slug])

    @property
    def discount(self):
        if not self.original_price:
            return 0
        return round(100 * (self.original_price - self.price) / self.original_price)

    @property
    def inclusion_list(self):
        return [line.strip() for line in self.t.inclusions.splitlines() if line.strip()]

    @property
    def paragraphs(self):
        return [p.strip() for p in self.t.description.split("\n\n") if p.strip()]

    @property
    def gallery_list(self):
        return [line.strip() for line in self.gallery.splitlines() if line.strip()]

    @property
    def is_open(self):
        return self.ends_at > timezone.now()

    @property
    def days_left(self):
        return max((self.ends_at - timezone.now()).days, 0)


class BookingRequest(models.Model):
    class Status(models.TextChoices):
        NEW = "new", _("New")
        CONFIRMED = "confirmed", _("Confirmed")
        CANCELLED = "cancelled", _("Cancelled")

    escape = models.ForeignKey(Escape, on_delete=models.CASCADE, related_name="requests")
    name = models.CharField(_("name"), max_length=120)
    email = models.EmailField(_("email"))
    phone = models.CharField(_("phone"), max_length=30, blank=True)
    check_in = models.DateField(_("arrival"))
    nights = models.PositiveSmallIntegerField(_("nights"), default=2)
    guests = models.PositiveSmallIntegerField(_("guests"), default=2)
    message = models.TextField(_("message"), blank=True)
    language = models.CharField(max_length=5, default="ru")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} · {self.escape.hotel_name} · {self.check_in}"

    @property
    def total(self):
        return self.escape.price * self.nights


class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    language = models.CharField(max_length=5, default="ru")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
