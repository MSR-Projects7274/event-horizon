from datetime import time, timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from events.models import Category, Event


class HomeViewTests(TestCase):
    """Tests for public home and about pages."""

    def setUp(self):
        self.category = Category.objects.create(name='Adventure')
        today = timezone.localdate()

        self.upcoming_event = Event.objects.create(
            category=self.category,
            name='Upcoming Event',
            description='An upcoming active event.',
            location='London',
            date=today + timedelta(days=1),
            time=time(18, 0),
            price=Decimal('20.00'),
            capacity=20,
            active=True,
        )
        self.past_event = Event.objects.create(
            category=self.category,
            name='Past Event',
            description='An event in the past.',
            location='London',
            date=today - timedelta(days=1),
            time=time(18, 0),
            price=Decimal('20.00'),
            capacity=20,
            active=True,
        )
        self.inactive_event = Event.objects.create(
            category=self.category,
            name='Inactive Event',
            description='An inactive event.',
            location='London',
            date=today + timedelta(days=2),
            time=time(18, 0),
            price=Decimal('20.00'),
            capacity=20,
            active=False,
        )

    def test_home_page_loads(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/index.html')

    def test_home_shows_only_active_upcoming_events(self):
        response = self.client.get(reverse('home'))
        upcoming_events = list(response.context['upcoming_events'])

        self.assertIn(self.upcoming_event, upcoming_events)
        self.assertNotIn(self.past_event, upcoming_events)
        self.assertNotIn(self.inactive_event, upcoming_events)

    def test_home_limits_featured_events_to_six(self):
        today = timezone.localdate()

        for index in range(7):
            Event.objects.create(
                category=self.category,
                name=f'Featured Event {index}',
                description='Featured event.',
                location='London',
                date=today + timedelta(days=index + 3),
                time=time(18, 0),
                price=Decimal('20.00'),
                capacity=20,
                active=True,
            )

        response = self.client.get(reverse('home'))

        self.assertEqual(len(response.context['featured_events']), 6)

    def test_about_page_loads(self):
        response = self.client.get(reverse('about'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/about.html')
