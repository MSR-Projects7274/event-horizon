import stripe

from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse

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

    # Only process completed Checkout Sessions

    if stripe_event['type'] != 'checkout.session.completed':
        return HttpResponse(status=200)

    session = stripe_event['data']['object']

    customer_details = session.customer_details.to_dict()

    customer_email = customer_details.get('email')

    # Make sure the payment was successful

    if session.payment_status != 'paid':
        return HttpResponse(status=200)

    # Retrieve booking information

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

    # Stripe Checkout Session ID

    session_id = session.id

    if not session_id:
        return HttpResponse(status=400)

    # Prevent duplicate bookings

    if Booking.objects.filter(
        stripe_session_id=session_id
    ).exists():
        return HttpResponse(status=200)

    # Check capacity and create booking

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

    # Send booking confirmation email

    if customer_email:
        total_price = event.price * quantity

        email_context = {
            'event': event,
            'quantity': quantity,
            'total_price': total_price,
            'bookings_url': request.build_absolute_uri(
                reverse('profile')
                ),
        }

        html_message = render_to_string(
            'emails/booking_confirmation.html',
            email_context,
        )

        plain_message = (
            f'Your booking for {event.name} is confirmed.\n\n'
            f'Date: {event.date:%d %B %Y}\n'
            f'Time: {event.time:%H:%M}\n'
            f'Location: {event.location}\n'
            f'Places: {quantity}\n'
            f'Price per place: £{event.price:.2f}\n'
            f'Total paid: £{total_price:.2f}\n\n'
            'Thank you for booking with Event Horizon.\n\n'
            'Discover experiences beyond the ordinary.'
        )

        send_mail(
            subject='Your Event Horizon booking is confirmed',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[customer_email],
            html_message=html_message,
        )
    return HttpResponse(status=200)