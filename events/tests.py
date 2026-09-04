from datetime import time, timedelta
from decimal import Decimal
from smtplib import SMTPDataError
from types import SimpleNamespace
from unittest.mock import call, patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Booking, Category, Event


class EventModelTests(TestCase):
    """Tests for event and booking model behaviour."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='pixel',
            password='StrongPass123!',
        )
        self.category = Category.objects.create(name='Adventure')
        self.event = Event.objects.create(
            category=self.category,
            name='Kayaking Experience',
            description='Take to the water.',
            location='River Centre',
            date=timezone.localdate() + timedelta(days=7),
            time=time(10, 0),
            price=Decimal('30.00'),
            capacity=10,
        )

    def test_category_string_representation(self):
        self.assertEqual(str(self.category), 'Adventure')

    def test_event_string_representation(self):
        self.assertEqual(str(self.event), 'Kayaking Experience')

    def test_places_booked_counts_only_confirmed_bookings(self):
        Booking.objects.create(
            user=self.user,
            event=self.event,
            quantity=3,
            stripe_session_id='cs_confirmed',
            status='confirmed',
        )
        Booking.objects.create(
            user=self.user,
            event=self.event,
            quantity=2,
            stripe_session_id='cs_cancelled',
            status='cancelled',
        )

        self.assertEqual(self.event.places_booked, 3)
        self.assertEqual(self.event.places_remaining, 7)

    def test_booking_total_price(self):
        booking = Booking.objects.create(
            user=self.user,
            event=self.event,
            quantity=2,
            stripe_session_id='cs_total',
        )

        self.assertEqual(booking.total_price, Decimal('60.00'))
        self.assertEqual(str(booking), 'pixel - Kayaking Experience')


class EventViewTests(TestCase):
    """Tests for event discovery and booking views."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='pixel',
            email='pixel@example.com',
            password='StrongPass123!',
        )
        self.other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='StrongPass123!',
        )
        self.adventure = Category.objects.create(name='Adventure')
        self.workshops = Category.objects.create(name='Workshops')
        self.event = Event.objects.create(
            category=self.adventure,
            name='Hidden History Walking Tour',
            description='Explore hidden streets.',
            location='York',
            date=timezone.localdate() + timedelta(days=5),
            time=time(18, 0),
            price=Decimal('18.00'),
            capacity=5,
            active=True,
        )
        self.workshop = Event.objects.create(
            category=self.workshops,
            name='Pottery Workshop',
            description='Make something by hand.',
            location='Leeds',
            date=timezone.localdate() + timedelta(days=6),
            time=time(19, 0),
            price=Decimal('25.00'),
            capacity=8,
            active=True,
        )
        self.inactive_event = Event.objects.create(
            category=self.adventure,
            name='Inactive Event',
            description='Hidden from visitors.',
            location='York',
            date=timezone.localdate() + timedelta(days=7),
            time=time(20, 0),
            price=Decimal('10.00'),
            capacity=5,
            active=False,
        )

    def test_event_list_shows_only_active_events(self):
        response = self.client.get(reverse('event_list'))
        events = list(response.context['events'])

        self.assertIn(self.event, events)
        self.assertIn(self.workshop, events)
        self.assertNotIn(self.inactive_event, events)

    def test_event_list_searches_name_description_location_and_category(self):
        for query in ('History', 'streets', 'York', 'Adventure'):
            with self.subTest(query=query):
                response = self.client.get(reverse('event_list'), {'q': query})
                self.assertIn(self.event, list(response.context['events']))

    def test_event_list_filters_by_category(self):
        response = self.client.get(
            reverse('event_list'),
            {'category': self.workshops.id},
        )
        events = list(response.context['events'])

        self.assertEqual(events, [self.workshop])

    def test_inactive_event_detail_returns_404(self):
        response = self.client.get(
            reverse('event_detail', args=[self.inactive_event.id])
        )

        self.assertEqual(response.status_code, 404)

    def test_book_event_requires_login(self):
        url = reverse('book_event', args=[self.event.id])
        response = self.client.get(url)

        self.assertRedirects(response, f"{reverse('login')}?next={url}")

    def test_book_event_displays_form_for_available_event(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('book_event', args=[self.event.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'events/book_event.html')
        self.assertEqual(response.context['event'], self.event)
        self.assertIn('form', response.context)

    def test_book_event_redirects_when_sold_out(self):
        Booking.objects.create(
            user=self.user,
            event=self.event,
            quantity=self.event.capacity,
            stripe_session_id='cs_sold_out',
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse('book_event', args=[self.event.id]))

        self.assertRedirects(
            response,
            reverse('event_detail', args=[self.event.id]),
        )

    def test_book_event_rejects_post_requests(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('book_event', args=[self.event.id]),
            {'quantity': 1},
        )

        self.assertEqual(response.status_code, 405)

    def test_user_cannot_cancel_another_users_booking(self):
        booking = Booking.objects.create(
            user=self.other_user,
            event=self.event,
            quantity=1,
            stripe_session_id='cs_other_booking',
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse('cancel_booking', args=[booking.id]))

        self.assertEqual(response.status_code, 404)

    @patch('events.views.send_mail')
    @patch('events.views.stripe.Refund.create')
    @patch('events.views.stripe.checkout.Session.retrieve')
    def test_cancel_booking_refunds_and_marks_booking_cancelled(
        self,
        mock_retrieve,
        mock_refund,
        mock_send_mail,
    ):
        booking = Booking.objects.create(
            user=self.user,
            event=self.event,
            quantity=2,
            stripe_session_id='cs_cancel_me',
        )
        mock_retrieve.return_value = SimpleNamespace(payment_intent='pi_123')
        mock_refund.return_value = SimpleNamespace(id='re_123')
        self.client.force_login(self.user)

        response = self.client.post(reverse('cancel_booking', args=[booking.id]))

        self.assertRedirects(response, reverse('profile'))
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'cancelled')
        self.assertEqual(booking.stripe_refund_id, 're_123')
        self.assertIsNotNone(booking.cancelled_at)
        mock_refund.assert_called_once_with(
            payment_intent='pi_123',
            idempotency_key=f'booking-cancellation-{booking.id}',
        )
        mock_send_mail.assert_called_once()

    @patch('events.views.send_mail')
    @patch('events.views.stripe.Refund.create')
    @patch('events.views.stripe.checkout.Session.retrieve')
    def test_cancel_booking_retry_reuses_same_refund_idempotency_key(
        self,
        mock_retrieve,
        mock_refund,
        mock_send_mail,
    ):
        booking = Booking.objects.create(
            user=self.user,
            event=self.event,
            quantity=2,
            stripe_session_id='cs_retry_cancel',
        )

        mock_retrieve.return_value = SimpleNamespace(
            payment_intent='pi_retry'
        )
        mock_refund.return_value = SimpleNamespace(
            id='re_retry'
        )

        self.client.force_login(self.user)

        original_save = Booking.save
        save_attempts = {'count': 0}

        def flaky_save(instance, *args, **kwargs):
            if save_attempts['count'] == 0:
                save_attempts['count'] += 1
                raise RuntimeError('Simulated local save failure')

            return original_save(instance, *args, **kwargs)

        with patch.object(
            Booking,
            'save',
            autospec=True,
            side_effect=flaky_save,
        ):
            with self.assertRaises(RuntimeError):
                self.client.post(
                    reverse(
                        'cancel_booking',
                        args=[booking.id],
                    )
                )

            response = self.client.post(
                reverse(
                    'cancel_booking',
                    args=[booking.id],
                )
            )

        self.assertRedirects(
            response,
            reverse('profile'),
        )

        booking.refresh_from_db()

        self.assertEqual(
            booking.status,
            'cancelled',
        )
        self.assertEqual(
            booking.stripe_refund_id,
            're_retry',
        )

        self.assertEqual(
            mock_refund.call_count,
            2,
        )

        expected_call = call(
            payment_intent='pi_retry',
            idempotency_key=(
                f'booking-cancellation-{booking.id}'
            ),
        )

        self.assertEqual(
            mock_refund.call_args_list,
            [
                expected_call,
                expected_call,
            ],
        )

        mock_send_mail.assert_called_once()

    @patch('events.views.send_mail')
    @patch('events.views.stripe.Refund.create')
    @patch('events.views.stripe.checkout.Session.retrieve')
    def test_cancel_booking_still_succeeds_when_email_fails(
        self,
        mock_retrieve,
        mock_refund,
        mock_send_mail,
    ):
        booking = Booking.objects.create(
            user=self.user,
            event=self.event,
            quantity=2,
            stripe_session_id='cs_email_failure',
        )
        mock_retrieve.return_value = SimpleNamespace(payment_intent='pi_456')
        mock_refund.return_value = SimpleNamespace(id='re_456')
        mock_send_mail.side_effect = SMTPDataError(
            550,
            b'Invalid recipient',
        )
        self.client.force_login(self.user)

        response = self.client.post(reverse('cancel_booking', args=[booking.id]))

        self.assertRedirects(response, reverse('profile'))
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'cancelled')
        self.assertEqual(booking.stripe_refund_id, 're_456')
        self.assertIsNotNone(booking.cancelled_at)
        mock_refund.assert_called_once_with(
            payment_intent='pi_456',
            idempotency_key=f'booking-cancellation-{booking.id}',
        )
        mock_send_mail.assert_called_once()
