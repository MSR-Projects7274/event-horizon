import stripe

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

from events.models import Event


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

    amount = int(
        event.price * 100
    )

    checkout_session = stripe.checkout.Session.create(
        mode='payment',

        line_items=[
            {
                'price_data': {
                    'currency': 'gbp',

                    'product_data': {
                        'name': event.name,
                        'description': event.description,
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
                '/bookings/success/'
            )
            + '?session_id={CHECKOUT_SESSION_ID}'
        ),

        cancel_url=request.build_absolute_uri(
            f'/events/{event.id}/'
        ),
    )

    return redirect(
        checkout_session.url
    )