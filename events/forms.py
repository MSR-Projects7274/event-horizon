from django import forms

from .models import Booking


class BookingForm(forms.ModelForm):
    """Form for booking places at an event."""

    class Meta:
        model = Booking
        fields = ['quantity']

        widgets = {
            'quantity': forms.NumberInput(
                attrs={
                    'min': 1,
                    'class': 'booking-quantity',
                }
            ),
        }