from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render

from events.models import Booking


def register(request):
    """Register a new user."""

    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            return redirect('login')

    else:
        form = UserCreationForm()

    return render(
        request,
        'registration/register.html',
        {'form': form}
    )

@login_required
def profile(request):
    """Display the user's profile and bookings."""

    bookings = Booking.objects.filter(
        user=request.user
    ).select_related(
        'event',
        'event__category'
    ).order_by(
        'event__date',
        'event__time'
    )

    return render(
        request,
        'profiles/profile.html',
        {
            'bookings': bookings,
        }
    )