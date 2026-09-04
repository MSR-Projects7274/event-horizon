import logging
from smtplib import SMTPException

import stripe

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET

from .forms import BookingForm
from .models import Booking, Category, Event

stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)


def event_list(request):
    """Display active events with search and category filtering."""

    search_query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category')

    events = Event.objects.filter(
        active=True
    ).select_related('category')

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
        active=True,
    )

    return render(
        request,
        'events/event_detail.html',
        {'event': event}
    )


@login_required
@require_GET
def book_event(request, event_id):
    """Display the booking form before payment."""

    event = get_object_or_404(
        Event,
        id=event_id,
        active=True,
    )

    if event.places_remaining <= 0:
        return redirect(
            'event_detail',
            event_id=event.id,
        )

    form = BookingForm()

    return render(
        request,
        'events/book_event.html',
        {
            'event': event,
            'form': form,
        }
    )


@login_required
def cancel_booking(request, booking_id):
    """Cancel a booking, refund the customer through Stripe,
    and send a cancellation email.
    """

    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )

    if booking.status == 'cancelled':
        return redirect('profile')

    if request.method == 'POST':

        try:
            session = stripe.checkout.Session.retrieve(
                booking.stripe_session_id
            )

            payment_intent = session.payment_intent

            if not payment_intent:
                return render(
                    request,
                    'events/cancel_booking.html',
                    {
                        'booking': booking,
                        'error_message': (
                            'Unable to find the payment for this booking. '
                            'Please contact us before cancelling.'
                        ),
                    }
                )

            refund = stripe.Refund.create(
                payment_intent=payment_intent,
                idempotency_key=f'booking-cancellation-{booking.id}',
            )

            booking.status = 'cancelled'
            booking.stripe_refund_id = refund.id
            booking.cancelled_at = timezone.now()

            booking.save(
                update_fields=[
                    'status',
                    'stripe_refund_id',
                    'cancelled_at',
                ]
            )

            # Send cancellation email

            customer_email = request.user.email

            if customer_email:
                total_price = booking.total_price

                email_context = {
                    'booking': booking,
                    'event': booking.event,
                    'quantity': booking.quantity,
                    'total_price': total_price,
                    'refund': refund,
                    'bookings_url': request.build_absolute_uri(
                        reverse('profile')
                    ),
                }

                html_message = render_to_string(
                    'emails/booking_cancellation.html',
                    email_context,
                )

                plain_message = (
                    f'Your Event Horizon booking has been cancelled.\n\n'
                    f'Event: {booking.event.name}\n'
                    f'Date: {booking.event.date:%d %B %Y}\n'
                    f'Time: {booking.event.time:%H:%M}\n'
                    f'Location: {booking.event.location}\n'
                    f'Places: {booking.quantity}\n\n'
                    f'Refund amount: £{total_price:.2f}\n'
                    f'Refund reference: {refund.id}\n\n'
                    'Your booking has been cancelled and your refund '
                    'has been requested through Stripe.\n\n'
                    'Thank you for choosing Event Horizon.'
                )

                try:
                    send_mail(
                        subject='Your Event Horizon booking has been cancelled',
                        message=plain_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[customer_email],
                        html_message=html_message,
                    )
                except (SMTPException, OSError):
                    logger.exception(
                        'Cancellation email failed for booking %s',
                        booking.id,
                    )

            return redirect('profile')

        except stripe.error.StripeError:
            return render(
                request,
                'events/cancel_booking.html',
                {
                    'booking': booking,
                    'error_message': (
                        'We could not process your refund. '
                        'Your booking has not been cancelled. '
                        'Please try again or contact us.'
                    ),
                }
            )

    return render(
        request,
        'events/cancel_booking.html',
        {
            'booking': booking,
        }
    )
