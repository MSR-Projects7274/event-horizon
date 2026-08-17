from django.db import models
from django.shortcuts import get_object_or_404, render

from .models import Category, Event


def event_list(request):
    """Display active events with search and category filtering."""

    search_query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category')

    events = Event.objects.filter(active=True)
    categories = Category.objects.all()

    if search_query:
        events = events.filter(
            models.Q(name__icontains=search_query) |
            models.Q(description__icontains=search_query) |
            models.Q(location__icontains=search_query) |
            models.Q(category__name__icontains=search_query)
        )

    if category_id:
        events = events.filter(category_id=category_id)

    return render(
        request,
        'events/event_list.html',
        {
            'events': events,
            'categories': categories,
            'selected_category': category_id,
            'search_query': search_query,
        }
    )


def event_detail(request, event_id):
    """Display the details of a single event."""

    event = get_object_or_404(
        Event,
        id=event_id,
        active=True
    )

    return render(
        request,
        'events/event_detail.html',
        {'event': event}
    )


def event_detail(request, event_id):
    """Display the details of a single event."""
    event = get_object_or_404(
        Event,
        id=event_id,
        active=True
    )

    return render(
        request,
        'events/event_detail.html',
        {'event': event}
    )