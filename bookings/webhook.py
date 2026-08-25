import stripe

from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from events.models import Event, Booking


stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
def stripe_webhook(request):
    """Handle webhook events sent from Stripe."""

    payload = request.body
    signature = request.META.get(
        'HTTP_STRIPE_SIGNATURE'
    )

    try:
        stripe_event = stripe.Webhook.construct_event(
            payload,
            signature,
            settings.STRIPE_WH_SECRET,
        )

    except ValueError:
        return HttpResponse(status=400)

    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    # --------------------------------------------------
    # Only process completed Checkout Sessions
    # --------------------------------------------------

    if stripe_event['type'] != 'checkout.session.completed':
        return HttpResponse(status=200)

    session = stripe_event['data']['object']

    # --------------------------------------------------
    # Make sure the payment was successful
    # --------------------------------------------------

    if session.payment_status != 'paid':
        return HttpResponse(status=200)

    # --------------------------------------------------
    # Retrieve booking information
    # --------------------------------------------------

    metadata = session.metadata.to_dict()

    event_id = metadata.get('event_id')
    user_id = metadata.get('user_id')
    quantity = metadata.get('quantity')

    if not event_id or not user_id or not quantity:
        return HttpResponse(status=400)

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return HttpResponse(status=400)

    if quantity < 1:
        return HttpResponse(status=400)

    # --------------------------------------------------
    # Stripe Checkout Session ID
    # --------------------------------------------------

    session_id = session.id

    if not session_id:
        return HttpResponse(status=400)

    # --------------------------------------------------
    # Prevent duplicate bookings
    # --------------------------------------------------

    if Booking.objects.filter(
        stripe_session_id=session_id
    ).exists():
        return HttpResponse(status=200)

    # --------------------------------------------------
    # Check capacity and create booking
    # --------------------------------------------------

    try:

        with transaction.atomic():

            event = Event.objects.select_for_update().get(
                id=event_id,
                active=True,
            )

            if quantity > event.places_remaining:
                return HttpResponse(status=400)

            Booking.objects.create(
                user_id=user_id,
                event=event,
                quantity=quantity,
                stripe_session_id=session_id,
            )

    except Event.DoesNotExist:
        return HttpResponse(status=400)

    return HttpResponse(status=200)