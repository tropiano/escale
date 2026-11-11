from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import get_language
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from .forms import BookingRequestForm, SubscribeForm
from .models import Destination, Escape, Subscriber


def open_escapes():
    return (
        Escape.objects.filter(is_published=True, ends_at__gt=timezone.now())
        .select_related("destination")
    )


def home(request):
    escapes = open_escapes()
    return render(request, "stays/home.html", {
        "hero": escapes.filter(is_featured=True).first() or escapes.first(),
        "featured": escapes[:6],
        "destinations": Destination.objects.annotate(
            n=Count("escapes", filter=Q(escapes__is_published=True, escapes__ends_at__gt=timezone.now()))
        ),
        "moods": Escape.Mood.choices,
    })


def escape_list(request):
    escapes = open_escapes()
    city = request.GET.get("city", "")
    mood = request.GET.get("mood", "")
    q = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "")

    if city:
        escapes = escapes.filter(destination__slug=city)
    if mood:
        escapes = escapes.filter(mood=mood)
    if q:
        escapes = escapes.filter(
            Q(hotel_name__icontains=q) | Q(hotel_name_en__icontains=q)
            | Q(destination__name__icontains=q) | Q(destination__name_en__icontains=q)
            | Q(title__icontains=q) | Q(title_en__icontains=q)
            | Q(neighbourhood__icontains=q) | Q(neighbourhood_en__icontains=q)
        )
    if sort == "price":
        escapes = escapes.order_by("price")
    elif sort == "ending":
        escapes = escapes.order_by("ends_at")

    return render(request, "stays/escape_list.html", {
        "escapes": escapes,
        "destinations": Destination.objects.all(),
        "moods": Escape.Mood.choices,
        "city": city, "mood": mood, "q": q, "sort": sort,
    })


def destination_detail(request, slug):
    destination = get_object_or_404(Destination, slug=slug)
    return render(request, "stays/destination.html", {
        "destination": destination,
        "escapes": open_escapes().filter(destination=destination),
        "others": Destination.objects.exclude(pk=destination.pk)[:4],
    })


def escape_detail(request, slug):
    escape = get_object_or_404(Escape.objects.select_related("destination"), slug=slug, is_published=True)
    form = BookingRequestForm(request.POST or None, escape=escape,
                              initial={"nights": max(2, escape.min_nights), "guests": 2})
    if request.method == "POST" and escape.is_open and form.is_valid():
        booking = form.save(commit=False)
        booking.escape = escape
        booking.language = get_language()
        booking.save()
        return render(request, "stays/booking_done.html", {"escape": escape, "booking": booking})

    return render(request, "stays/escape_detail.html", {
        "escape": escape,
        "form": form,
        "similar": open_escapes().exclude(pk=escape.pk).filter(
            Q(destination=escape.destination) | Q(mood=escape.mood)
        )[:3],
    })


@require_POST
def subscribe(request):
    form = SubscribeForm(request.POST)
    if form.is_valid():
        Subscriber.objects.get_or_create(
            email=form.cleaned_data["email"].lower(), defaults={"language": get_language()}
        )
        messages.success(request, _("Welcome to the club. Our next private sales will land in your inbox."))
    else:
        messages.error(request, _("Please enter a valid email address."))
    next_url = request.POST.get("next", "")
    if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        next_url = "stays:home"
    return redirect(next_url)


def about(request):
    return render(request, "stays/about.html")
