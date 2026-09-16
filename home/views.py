from django.db import models
from django.shortcuts import redirect, render
from django.urls import Resolver404
from django.views.defaults import page_not_found
from django.utils import timezone

from events.models import Event


def home(request):
    """Display the Event Horizon homepage."""

    now = timezone.localtime()
    current_date = now.date()
    current_time = now.time().replace(tzinfo=None)

    upcoming_filter = models.Q(date__gt=current_date)
    upcoming_filter.add(
        models.Q(
            date=current_date,
            time__gt=current_time,
        ),
        models.Q.OR,
    )

    upcoming_events = Event.objects.filter(
        active=True
    ).filter(
        upcoming_filter
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


def redirect_not_found(request, exception):
    """Redirect unknown URLs while preserving resource 404 responses."""

    if isinstance(exception, Resolver404):
        return redirect('home')

    return page_not_found(request, exception)
