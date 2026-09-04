import logging
from smtplib import SMTPException

import stripe

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from events.models import Booking, Event

stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)
User = get_user_model()


def refund_unfulfillable_booking(booking, payment_intent):
    """Refund a paid booking that can no longer be fulfilled."""

    try:
        refund = stripe.Refund.create(
            payment_intent=payment_intent,
            idempotency_key=(
                f'capacity-refund-{booking.stripe_session_id}'
            ),
        )
    except stripe.error.StripeError:
        return False

    booking.stripe_refund_id = refund.id
    booking.cancelled_at = timezone.now()

    booking.save(
        update_fields=[
            'stripe_refund_id',
            'cancelled_at',
        ]
    )

    return True


def refund_unfulfillable_payment(
    session_id,
    payment_intent,
    idempotency_prefix,
):
    """Refund a paid session that cannot be fulfilled."""

    try:
        stripe.Refund.create(
            payment_intent=payment_intent,
            idempotency_key=(
                f'{idempotency_prefix}-{session_id}'
            ),
        )
    except stripe.error.StripeError:
        return False

    return True


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
    payment_intent = session.payment_intent

    if not session_id:
        return HttpResponse(status=400)

    # Make sure the booking user still exists

    try:
        user_exists = User.objects.filter(
            pk=user_id,
        ).exists()
    except (TypeError, ValueError):
        return HttpResponse(status=400)

    if not user_exists:
        if not payment_intent:
            return HttpResponse(status=500)

        if refund_unfulfillable_payment(
            session_id,
            payment_intent,
            'missing-user-refund',
        ):
            return HttpResponse(status=200)

        return HttpResponse(status=500)

    # Prevent duplicate bookings already processed

    existing_booking = Booking.objects.filter(
        stripe_session_id=session_id
    ).first()

    if existing_booking:
        if (
            existing_booking.status == 'cancelled'
            and not existing_booking.stripe_refund_id
        ):
            if not payment_intent:
                return HttpResponse(status=500)

            if refund_unfulfillable_booking(
                existing_booking,
                payment_intent,
            ):
                return HttpResponse(status=200)

            return HttpResponse(status=500)

        return HttpResponse(status=200)

    # Lock the event, recheck for concurrent webhook delivery,
    # then check capacity and create the booking.

    try:

        with transaction.atomic():

            event = Event.objects.select_for_update().get(
                id=event_id,
                active=True,
            )

            concurrent_booking = Booking.objects.filter(
                stripe_session_id=session_id,
            ).first()

            if concurrent_booking:
                booking = None

            elif quantity > event.places_remaining:
                booking = Booking.objects.create(
                    user_id=user_id,
                    event=event,
                    quantity=quantity,
                    stripe_session_id=session_id,
                    status='cancelled',
                )

            else:
                Booking.objects.create(
                    user_id=user_id,
                    event=event,
                    quantity=quantity,
                    stripe_session_id=session_id,
                )

                booking = None

    except Event.DoesNotExist:
        if not payment_intent:
            return HttpResponse(status=500)

        if refund_unfulfillable_payment(
            session_id,
            payment_intent,
            'unavailable-event-refund',
        ):
            return HttpResponse(status=200)

        return HttpResponse(status=500)

    # A duplicate webhook may have created the booking while this
    # request was waiting for the event lock.

    if concurrent_booking:
        if (
            concurrent_booking.status == 'cancelled'
            and not concurrent_booking.stripe_refund_id
        ):
            if not payment_intent:
                return HttpResponse(status=500)

            if refund_unfulfillable_booking(
                concurrent_booking,
                payment_intent,
            ):
                return HttpResponse(status=200)

            return HttpResponse(status=500)

        return HttpResponse(status=200)

    # Refund if capacity disappeared after payment

    if booking:
        if not payment_intent:
            return HttpResponse(status=500)

        if refund_unfulfillable_booking(
            booking,
            payment_intent,
        ):
            return HttpResponse(status=200)

        return HttpResponse(status=500)

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

        try:
            send_mail(
                subject='Your Event Horizon booking is confirmed',
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[customer_email],
                html_message=html_message,
            )
        except (SMTPException, OSError):
            logger.exception(
                'Booking confirmation email failed for Stripe session %s',
                session_id,
            )

    return HttpResponse(status=200)
