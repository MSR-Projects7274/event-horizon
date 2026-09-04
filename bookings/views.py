import stripe

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from events.models import Booking, Event

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def create_checkout_session(request, event_id):
    """Create a Stripe Checkout Session for an event booking."""

    event = get_object_or_404(
        Event,
        id=event_id,
        active=True,
    )

    if request.method != 'POST':
        return redirect(
            'event_detail',
            event_id=event.id,
        )

    try:
        quantity = int(
            request.POST.get('quantity', 0)
        )
    except (TypeError, ValueError):
        quantity = 0

    if quantity < 1:
        return redirect(
            'event_detail',
            event_id=event.id,
        )

    if quantity > event.places_remaining:
        return redirect(
            'event_detail',
            event_id=event.id,
        )

    if not request.user.email:
        return redirect('edit_profile')

    amount = int(
        event.price * 100
    )

    try:
        checkout_session = stripe.checkout.Session.create(
            mode='payment',
            customer_email=request.user.email,
            line_items=[
                {
                    'price_data': {
                        'currency': 'gbp',
                        'product_data': {
                            'name': event.name,
                            'description': (
                                f'{event.date:%d %B %Y} at '
                                f'{event.time:%H:%M} • '
                                f'{event.location}'
                            ),
                        },
                        'unit_amount': amount,
                    },
                    'quantity': quantity,
                }
            ],
            metadata={
                'event_id': str(event.id),
                'user_id': str(request.user.id),
                'quantity': str(quantity),
            },
            success_url=(
                request.build_absolute_uri(
                    reverse('booking_success')
                )
                + '?session_id={CHECKOUT_SESSION_ID}'
            ),
            cancel_url=request.build_absolute_uri(
                reverse(
                    'event_detail',
                    kwargs={'event_id': event.id},
                )
            ),
        )
    except stripe.error.StripeError:
        return redirect(
            'event_detail',
            event_id=event.id,
        )

    return redirect(
        checkout_session.url
    )


@login_required
def booking_success(request):
    """Display the booking confirmation after successful payment."""

    session_id = request.GET.get('session_id')

    if not session_id:
        return redirect('event_list')

    booking = Booking.objects.filter(
        stripe_session_id=session_id,
    ).first()

    if (
        booking is not None
        and booking.user_id != request.user.id
    ):
        raise Http404

    confirmed_booking = None
    cancelled_booking = None

    if booking is not None:
        if booking.status == 'cancelled':
            cancelled_booking = booking
        else:
            confirmed_booking = booking

    return render(
        request,
        'bookings/booking_success.html',
        {
            'booking': confirmed_booking,
            'cancelled_booking': cancelled_booking,
            'session_id': session_id,
        }
    )
