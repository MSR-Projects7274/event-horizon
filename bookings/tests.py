from datetime import time, timedelta
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

import stripe

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from events.models import Booking, Category, Event


class StripeDict(dict):
    """Minimal Stripe-like mapping used by webhook tests."""

    def to_dict(self):
        return dict(self)


class CheckoutViewTests(TestCase):
    """Tests for creating Stripe Checkout sessions and success pages."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='pixel',
            email='pixel@example.com',
            password='StrongPass123!',
        )
        self.category = Category.objects.create(name='Music & Entertainment')
        self.event = Event.objects.create(
            category=self.category,
            name='Live Acoustic Night',
            description='An evening of live music.',
            location='The Venue',
            date=timezone.localdate() + timedelta(days=10),
            time=time(20, 0),
            price=Decimal('12.50'),
            capacity=5,
            active=True,
        )

    def test_checkout_requires_login(self):
        url = reverse('create_checkout_session', args=[self.event.id])
        response = self.client.post(url, {'quantity': 1})

        self.assertRedirects(response, f"{reverse('login')}?next={url}")

    def test_checkout_get_redirects_to_event_detail(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('create_checkout_session', args=[self.event.id])
        )

        self.assertRedirects(
            response,
            reverse('event_detail', args=[self.event.id]),
        )

    @patch('bookings.views.stripe.checkout.Session.create')
    def test_checkout_rejects_invalid_quantity(self, mock_create):
        self.client.force_login(self.user)
        url = reverse('create_checkout_session', args=[self.event.id])

        for quantity in ('0', '-1', 'not-a-number'):
            with self.subTest(quantity=quantity):
                response = self.client.post(url, {'quantity': quantity})
                self.assertRedirects(
                    response,
                    reverse('event_detail', args=[self.event.id]),
                )

        mock_create.assert_not_called()

    @patch('bookings.views.stripe.checkout.Session.create')
    def test_checkout_rejects_quantity_above_remaining_capacity(
        self,
        mock_create,
    ):
        Booking.objects.create(
            user=self.user,
            event=self.event,
            quantity=4,
            stripe_session_id='cs_existing',
        )
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('create_checkout_session', args=[self.event.id]),
            {'quantity': 2},
        )

        self.assertRedirects(
            response,
            reverse('event_detail', args=[self.event.id]),
        )
        mock_create.assert_not_called()

    @patch('bookings.views.stripe.checkout.Session.create')
    def test_checkout_requires_user_email(self, mock_create):
        self.user.email = ''
        self.user.save(update_fields=['email'])
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('create_checkout_session', args=[self.event.id]),
            {'quantity': 1},
        )

        self.assertRedirects(response, reverse('edit_profile'))
        mock_create.assert_not_called()

    @patch('bookings.views.stripe.checkout.Session.create')
    def test_valid_checkout_uses_reversed_absolute_urls(self, mock_create):
        mock_create.return_value = SimpleNamespace(
            url='https://checkout.stripe.test/session'
        )
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('create_checkout_session', args=[self.event.id]),
            {'quantity': 2},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'],
            'https://checkout.stripe.test/session',
        )
        kwargs = mock_create.call_args.kwargs
        self.assertEqual(kwargs['mode'], 'payment')
        self.assertEqual(kwargs['customer_email'], self.user.email)
        self.assertEqual(kwargs['line_items'][0]['quantity'], 2)
        self.assertEqual(kwargs['line_items'][0]['price_data']['unit_amount'], 1250)
        self.assertEqual(kwargs['metadata']['event_id'], str(self.event.id))
        self.assertEqual(kwargs['metadata']['user_id'], str(self.user.id))
        self.assertEqual(kwargs['metadata']['quantity'], '2')
        self.assertEqual(
            kwargs['success_url'],
            'http://testserver/bookings/success/'
            '?session_id={CHECKOUT_SESSION_ID}',
        )
        self.assertEqual(
            kwargs['cancel_url'],
            f'http://testserver/events/{self.event.id}/',
        )

    def test_booking_success_requires_session_id(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('booking_success'))

        self.assertRedirects(response, reverse('event_list'))

    def test_booking_success_displays_users_booking(self):
        booking = Booking.objects.create(
            user=self.user,
            event=self.event,
            quantity=2,
            stripe_session_id='cs_success',
        )
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('booking_success'),
            {'session_id': booking.stripe_session_id},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/booking_success.html')
        self.assertEqual(response.context['booking'], booking)

    def test_booking_success_does_not_show_another_users_booking(self):
        other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='StrongPass123!',
        )
        booking = Booking.objects.create(
            user=other_user,
            event=self.event,
            quantity=1,
            stripe_session_id='cs_other_success',
        )
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('booking_success'),
            {'session_id': booking.stripe_session_id},
        )

        self.assertEqual(response.status_code, 404)


class WebhookTests(TestCase):
    """Tests for Stripe webhook validation, capacity and idempotency."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='pixel',
            email='pixel@example.com',
            password='StrongPass123!',
        )
        self.category = Category.objects.create(name='Adventure')
        self.event = Event.objects.create(
            category=self.category,
            name='Sunrise Hilltop Hike',
            description='Watch the sunrise.',
            location='The Hills',
            date=timezone.localdate() + timedelta(days=12),
            time=time(6, 0),
            price=Decimal('15.00'),
            capacity=5,
            active=True,
        )
        self.webhook_url = reverse('stripe_webhook')

    def stripe_session(
        self,
        *,
        session_id='cs_webhook',
        quantity='2',
        payment_status='paid',
        event_id=None,
        user_id=None,
        email=None,
    ):
        return SimpleNamespace(
            id=session_id,
            payment_status=payment_status,
            customer_details=StripeDict(
                email=email if email is not None else self.user.email
            ),
            metadata=StripeDict(
                event_id=str(event_id if event_id is not None else self.event.id),
                user_id=str(user_id if user_id is not None else self.user.id),
                quantity=quantity,
            ),
        )

    def stripe_event(self, session, event_type='checkout.session.completed'):
        return {
            'type': event_type,
            'data': {'object': session},
        }

    @patch('bookings.webhook.stripe.Webhook.construct_event')
    def test_webhook_rejects_malformed_payload(self, mock_construct_event):
        mock_construct_event.side_effect = ValueError('Invalid payload')

        response = self.client.post(
            self.webhook_url,
            data='not-json',
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test-signature',
        )

        self.assertEqual(response.status_code, 400)

    @patch('bookings.webhook.stripe.Webhook.construct_event')
    def test_webhook_rejects_invalid_signature(self, mock_construct_event):
        mock_construct_event.side_effect = stripe.error.SignatureVerificationError(
            'Invalid signature',
            'test-signature',
        )

        response = self.client.post(
            self.webhook_url,
            data='{}',
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test-signature',
        )

        self.assertEqual(response.status_code, 400)

    @patch('bookings.webhook.stripe.Webhook.construct_event')
    def test_webhook_ignores_unrelated_event_type(self, mock_construct_event):
        session = self.stripe_session()
        mock_construct_event.return_value = self.stripe_event(
            session,
            event_type='payment_intent.created',
        )

        response = self.client.post(
            self.webhook_url,
            data='{}',
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test-signature',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Booking.objects.count(), 0)

    @patch('bookings.webhook.stripe.Webhook.construct_event')
    def test_webhook_ignores_unpaid_checkout(self, mock_construct_event):
        session = self.stripe_session(payment_status='unpaid')
        mock_construct_event.return_value = self.stripe_event(session)

        response = self.client.post(
            self.webhook_url,
            data='{}',
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test-signature',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Booking.objects.count(), 0)

    @patch('bookings.webhook.send_mail')
    @patch('bookings.webhook.stripe.Webhook.construct_event')
    def test_paid_checkout_creates_booking_and_sends_email(
        self,
        mock_construct_event,
        mock_send_mail,
    ):
        session = self.stripe_session(quantity='2')
        mock_construct_event.return_value = self.stripe_event(session)

        response = self.client.post(
            self.webhook_url,
            data='{}',
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test-signature',
        )

        self.assertEqual(response.status_code, 200)
        booking = Booking.objects.get(stripe_session_id='cs_webhook')
        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.event, self.event)
        self.assertEqual(booking.quantity, 2)
        self.assertEqual(booking.status, 'confirmed')
        mock_send_mail.assert_called_once()

    @patch('bookings.webhook.send_mail')
    @patch('bookings.webhook.stripe.Webhook.construct_event')
    def test_duplicate_webhook_does_not_create_second_booking(
        self,
        mock_construct_event,
        mock_send_mail,
    ):
        Booking.objects.create(
            user=self.user,
            event=self.event,
            quantity=2,
            stripe_session_id='cs_webhook',
        )
        session = self.stripe_session(quantity='2')
        mock_construct_event.return_value = self.stripe_event(session)

        response = self.client.post(
            self.webhook_url,
            data='{}',
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test-signature',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Booking.objects.filter(stripe_session_id='cs_webhook').count(),
            1,
        )
        mock_send_mail.assert_not_called()

    @patch('bookings.webhook.stripe.Webhook.construct_event')
    def test_webhook_rejects_booking_above_remaining_capacity(
        self,
        mock_construct_event,
    ):
        Booking.objects.create(
            user=self.user,
            event=self.event,
            quantity=4,
            stripe_session_id='cs_existing_capacity',
        )
        session = self.stripe_session(
            session_id='cs_over_capacity',
            quantity='2',
        )
        mock_construct_event.return_value = self.stripe_event(session)

        response = self.client.post(
            self.webhook_url,
            data='{}',
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test-signature',
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(
            Booking.objects.filter(stripe_session_id='cs_over_capacity').exists()
        )
