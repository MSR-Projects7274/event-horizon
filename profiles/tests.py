from datetime import time, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from events.models import Booking, Category, Event


class RegistrationTests(TestCase):
    """Tests for account registration and anonymous-only access."""

    def test_registration_page_loads_for_anonymous_user(self):
        response = self.client.get(reverse('register'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')

    def test_authenticated_user_is_redirected_from_registration(self):
        user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='StrongPass123!',
        )
        self.client.force_login(user)

        response = self.client.get(reverse('register'))

        self.assertRedirects(response, reverse('home'))

    def test_valid_registration_creates_user(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'newuser',
                'email': 'new@example.com',
                'password1': 'StrongPass123!',
                'password2': 'StrongPass123!',
            },
        )

        self.assertRedirects(response, reverse('login'))
        self.assertTrue(
            User.objects.filter(
                username='newuser',
                email='new@example.com',
            ).exists()
        )

    def test_registration_requires_email(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'newuser',
                'email': '',
                'password1': 'StrongPass123!',
                'password2': 'StrongPass123!',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].has_error('email', 'required'))
        self.assertFalse(User.objects.filter(username='newuser').exists())

    def test_authenticated_user_is_redirected_from_login(self):
        user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='StrongPass123!',
        )
        self.client.force_login(user)

        response = self.client.get(reverse('login'))

        self.assertRedirects(response, reverse('home'))


class ProfileViewTests(TestCase):
    """Tests for protected profile functionality."""

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
        self.category = Category.objects.create(name='Workshops')
        self.event = Event.objects.create(
            category=self.category,
            name='Pottery Workshop',
            description='Learn pottery.',
            location='Studio',
            date=timezone.localdate() + timedelta(days=5),
            time=time(19, 0),
            price=Decimal('25.00'),
            capacity=20,
        )

    def test_profile_requires_login(self):
        response = self.client.get(reverse('profile'))

        expected_url = f"{reverse('login')}?next={reverse('profile')}"
        self.assertRedirects(response, expected_url)

    def test_profile_shows_only_current_users_bookings(self):
        own_booking = Booking.objects.create(
            user=self.user,
            event=self.event,
            quantity=2,
            stripe_session_id='cs_own',
        )
        other_booking = Booking.objects.create(
            user=self.other_user,
            event=self.event,
            quantity=1,
            stripe_session_id='cs_other',
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse('profile'))
        bookings = list(response.context['bookings'])

        self.assertIn(own_booking, bookings)
        self.assertNotIn(other_booking, bookings)

    def test_edit_profile_updates_email(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('edit_profile'),
            {'email': 'updated@example.com'},
        )

        self.assertRedirects(response, reverse('profile'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'updated@example.com')

    def test_change_password_keeps_user_logged_in(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('change_password'),
            {
                'old_password': 'StrongPass123!',
                'new_password1': 'EvenStrongerPass456!',
                'new_password2': 'EvenStrongerPass456!',
            },
        )

        self.assertRedirects(response, reverse('profile'))
        profile_response = self.client.get(reverse('profile'))
        self.assertEqual(profile_response.status_code, 200)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('EvenStrongerPass456!'))
