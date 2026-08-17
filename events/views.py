from django.shortcuts import get_object_or_404, render

from .models import Event


def event_list(request):
    """Display all active upcoming events."""
    events = Event.objects.filter(active=True)

    return render(
        request,
        'events/event_list.html',
        {'events': events}
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