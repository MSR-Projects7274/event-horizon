from django.shortcuts import render
from django.utils import timezone

from events.models import Event


def home(request):
    """Display the Event Horizon homepage."""

    today = timezone.localdate()

    upcoming_events = Event.objects.filter(
        active=True,
        date__gte=today,
    ).select_related('category').order_by(
        'date',
        'time',
    )

    featured_events = upcoming_events[:6]

    return render(
        request,
        'home/index.html',
        {
            'upcoming_events': upcoming_events,
            'featured_events': featured_events,
        },
    )


def about(request):
    """Display information about Event Horizon."""

    return render(
        request,
        'home/about.html',
    )
