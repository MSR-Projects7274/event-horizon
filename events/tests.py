from datetime import datetime, time, timedelta
from decimal import Decimal
from smtplib import SMTPDataError
from types import SimpleNamespace
from unittest.mock import call, patch

from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models.deletion import ProtectedError
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from .admin import BookingAdmin
from .models import Booking, Category, Event


class EventModelTests(TestCase):
    """Tests for event and booking model behaviour."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='test',
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

    @patch('events.models.timezone.now')
    def test_event_has_started_uses_scheduled_time(
        self,
        mock_now,
    ):
        event_start = timezone.make_aware(
            datetime.combine(
                self.event.date,
                self.event.time,
            ),
            timezone.get_current_timezone(),
        )

        mock_now.return_value = event_start - timedelta(minutes=1)

        self.assertFalse(self.event.has_started)

        mock_now.return_value = event_start

        self.assertTrue(self.event.has_started)

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
        self.assertEqual(str(booking), 'test - Kayaking Experience')

    def test_booking_quantity_cannot_be_zero(self):
        with self.assertRaises(IntegrityError):
            Booking.objects.create(
                user=self.user,
                event=self.event,
                quantity=0,
                stripe_session_id='cs_zero_quantity',
            )

    def test_event_price_must_be_positive_during_validation(self):
        self.event.price = Decimal('0.00')

        with self.assertRaises(ValidationError):
            self.event.full_clean()

    def test_event_price_cannot_be_zero_in_database(self):
        with self.assertRaises(IntegrityError):
            Event.objects.create(
                category=self.category,
                name='Free Invalid Event',
                description='Invalid zero-price event.',
                location='Test Venue',
                date=timezone.localdate() + timedelta(days=8),
                time=time(12, 0),
                price=Decimal('0.00'),
                capacity=5,
            )

    def test_event_capacity_cannot_be_reduced_below_confirmed_bookings(self):
        Booking.objects.create(
            user=self.user,
            event=self.event,
            quantity=3,
            stripe_session_id='cs_capacity_protection',
            status='confirmed',
        )

        self.event.capacity = 2

        with self.assertRaises(ValidationError) as error:
            self.event.full_clean()

        self.assertIn(
            'capacity',
            error.exception.message_dict,
        )

    def test_event_with_booking_cannot_be_deleted(self):
        booking = Booking.objects.create(
            user=self.user,
            event=self.event,
            quantity=1,
            stripe_session_id='cs_protected_event',
        )

        with self.assertRaises(ProtectedError):
            self.event.delete()

        self.assertTrue(
            Event.objects.filter(pk=self.event.pk).exists()
        )
        self.assertTrue(
            Booking.objects.filter(pk=booking.pk).exists()
        )

    def test_category_with_event_cannot_be_deleted(self):
        with self.assertRaises(ProtectedError):
            self.category.delete()

        self.assertTrue(
            Category.objects.filter(pk=self.category.pk).exists()
        )
        self.assertTrue(
            Event.objects.filter(pk=self.event.pk).exists()
        )


class BookingAdminTests(TestCase):
    """Tests for protecting Stripe-managed bookings in Django Admin."""

    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='StrongPass123!',
        )
        self.request = RequestFactory().get('/admin/events/booking/')
        self.request.user = self.superuser
        self.booking_admin = BookingAdmin(
            Booking,
            AdminSite(),
        )

    def test_booking_admin_is_view_only(self):
        self.assertTrue(
            self.booking_admin.has_view_permission(
                self.request,
            )
        )
        self.assertFalse(
            self.booking_admin.has_add_permission(
                self.request,
            )
        )
        self.assertFalse(
            self.booking_admin.has_change_permission(
                self.request,
            )
        )
        self.assertFalse(
            self.booking_admin.has_delete_permission(
                self.request,
            )
        )


class EventViewTests(TestCase):
    """Tests for event discovery and booking views."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='test',
            email='test@example.com',
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

        self.past_event = Event.objects.create(
            category=self.adventure,
            name='Past Event',
            description='This event has already happened.',
            location='York',
            date=timezone.localdate() - timedelta(days=1),
            time=time(18, 0),
            price=Decimal('15.00'),
            capacity=5,
            active=True,
        )

    def test_event_list_shows_only_active_events(self):
        response = self.client.get(reverse('event_list'))
        events = list(response.context['events'])

        self.assertIn(self.event, events)
        self.assertIn(self.workshop, events)
        self.assertNotIn(self.inactive_event, events)

    def test_event_list_excludes_past_events(self):
        response = self.client.get(reverse('event_list'))

        events = list(response.context['events'])

        self.assertNotIn(self.past_event, events)

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

    def test_event_list_ignores_invalid_category_filter(self):
        response = self.client.get(
            reverse('event_list'),
            {'category': 'potato'},
        )

        self.assertEqual(response.status_code, 200)

        events = list(response.context['events'])

        self.assertIn(self.event, events)
        self.assertIn(self.workshop, events)
        self.assertIsNone(
            response.context['selected_category'],
        )

    def test_inactive_event_detail_returns_404(self):
        response = self.client.get(
            reverse('event_detail', args=[self.inactive_event.id])
        )

        self.assertEqual(response.status_code, 404)

    def test_past_event_detail_shows_ended_state_without_booking_link(self):
        response = self.client.get(
            reverse('event_detail', args=[self.past_event.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'This event has already taken place.',
        )
        self.assertContains(
            response,
            'Event Ended',
        )
        self.assertNotContains(
            response,
            reverse('book_event', args=[self.past_event.id]),
        )

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

    def test_book_event_redirects_when_event_has_started(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('book_event', args=[self.past_event.id])
        )

        self.assertRedirects(
            response,
            reverse('event_detail', args=[self.past_event.id]),
        )

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

    @patch('events.views.stripe.Refund.create')
    @patch('events.views.stripe.checkout.Session.retrieve')
    def test_cancel_booking_rejects_cancellation_after_event_has_started(
        self,
        mock_retrieve,
        mock_refund,
    ):
        booking = Booking.objects.create(
            user=self.user,
            event=self.past_event,
            quantity=1,
            stripe_session_id='cs_past_event_booking',
        )

        mock_retrieve.return_value = SimpleNamespace(
            payment_intent='pi_past_event'
        )
        mock_refund.return_value = SimpleNamespace(
            id='re_past_event'
        )

        self.client.force_login(self.user)

        response = self.client.post(
            reverse('cancel_booking', args=[booking.id])
        )

        self.assertRedirects(response, reverse('profile'))

        booking.refresh_from_db()

        self.assertEqual(booking.status, 'confirmed')
        self.assertIsNone(booking.stripe_refund_id)
        self.assertIsNone(booking.cancelled_at)

        mock_retrieve.assert_not_called()
        mock_refund.assert_not_called()

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
