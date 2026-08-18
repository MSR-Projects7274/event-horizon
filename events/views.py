from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BookingForm
from .models import Category, Event
from django.db import models


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
        request,'events/event_list.html',
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
        request,'events/event_detail.html',{'event': event}
    )


def event_detail(request, event_id):
    """Display the details of a single event."""
    event = get_object_or_404(
        Event, id=event_id, active=True)

    return render(
        request,
        'events/event_detail.html',
        {'event': event}
    )

@login_required
def book_event(request, event_id):
    """Allow an authenticated user to book places at an event."""

    event = get_object_or_404(
        Event, id=event_id, active=True)

    if event.places_remaining <= 0:
        return redirect('event_detail', event_id=event.id)

    if request.method == 'POST':
        form = BookingForm(request.POST)

        if form.is_valid():

            quantity = form.cleaned_data['quantity']

            if quantity > event.places_remaining:
                form.add_error(
                    'quantity',
                    f'Only {event.places_remaining} places are available.'
                )

            else:
                booking = form.save(commit=False)
                booking.user = request.user
                booking.event = event
                booking.save()

                return redirect(
                    'event_detail',
                    event_id=event.id
                )

    else:
        form = BookingForm()

    return render(
        request,
        'events/book_event.html',
        {
            'event': event,
            'form': form,
        }
    )