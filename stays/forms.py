from datetime import date

from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext

from .models import BookingRequest, Subscriber


class BookingRequestForm(forms.ModelForm):
    class Meta:
        model = BookingRequest
        fields = ["check_in", "nights", "guests", "name", "email", "phone", "message"]
        widgets = {
            "check_in": forms.DateInput(attrs={"type": "date"}),
            "message": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, escape=None, **kwargs):
        self.escape = escape
        super().__init__(*args, **kwargs)
        # Built per request so labels follow the active language.
        self.fields["nights"].widget = forms.Select(choices=[
            (n, ngettext("%(n)d night", "%(n)d nights", n) % {"n": n}) for n in range(1, 6)
        ])
        self.fields["guests"].widget = forms.Select(choices=[
            (n, ngettext("%(n)d guest", "%(n)d guests", n) % {"n": n}) for n in range(1, 5)
        ])
        self.fields["check_in"].widget.attrs["min"] = date.today().isoformat()
        self.fields["name"].widget.attrs["placeholder"] = _("Your name")
        self.fields["email"].widget.attrs["placeholder"] = "you@example.com"
        self.fields["phone"].widget.attrs["placeholder"] = "+7 900 000-00-00"
        self.fields["message"].label = _("A special touch? (optional)")
        self.fields["message"].widget.attrs["placeholder"] = _("An anniversary, a surprise, a late check-out…")

    def clean_check_in(self):
        value = self.cleaned_data["check_in"]
        if value < date.today():
            raise forms.ValidationError(_("Please choose a date in the future."))
        return value

    def clean_nights(self):
        value = self.cleaned_data["nights"]
        if self.escape and value < self.escape.min_nights:
            raise forms.ValidationError(
                ngettext("This escape starts at %(n)d night.", "This escape starts at %(n)d nights.",
                         self.escape.min_nights) % {"n": self.escape.min_nights}
            )
        return value


class SubscribeForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ["email"]

    def validate_unique(self):
        # Re-subscribing is fine; the view handles duplicates quietly.
        pass
