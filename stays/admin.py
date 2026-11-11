from django.contrib import admin

from .models import BookingRequest, Destination, Escape, Subscriber


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ("name", "name_en", "order")
    list_editable = ("order",)
    prepopulated_fields = {"slug": ("name_en",)}


@admin.register(Escape)
class EscapeAdmin(admin.ModelAdmin):
    list_display = ("hotel_name", "destination", "mood", "price", "original_price", "ends_at", "is_featured", "is_published")
    list_filter = ("destination", "mood", "is_featured", "is_published")
    list_editable = ("is_featured", "is_published")
    search_fields = ("hotel_name", "hotel_name_en", "title", "title_en")
    prepopulated_fields = {"slug": ("hotel_name_en",)}
    fieldsets = (
        ("Русский", {"fields": ("hotel_name", "title", "neighbourhood", "summary", "description", "inclusions")}),
        ("English", {"fields": ("hotel_name_en", "title_en", "neighbourhood_en", "summary_en", "description_en", "inclusions_en")}),
        ("Offer", {"fields": ("slug", "destination", "mood", "stars", "rating", "price", "original_price",
                              "min_nights", "ends_at", "is_featured", "is_published")}),
        ("Photos", {"fields": ("image_url", "gallery")}),
    )


@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "escape", "check_in", "nights", "guests", "status", "created_at")
    list_filter = ("status", "escape__destination", "language")
    list_editable = ("status",)
    search_fields = ("name", "email", "phone")


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "language", "created_at")
