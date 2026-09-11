from datetime import datetime
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Event(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='events'
    )

    name = models.CharField(max_length=200)

    description = models.TextField()

    location = models.CharField(max_length=255)

    date = models.DateField()

    time = models.TimeField()

    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal('0.01')),
        ],
    )

    capacity = models.PositiveIntegerField()

    image = models.ImageField(
        upload_to='events/',
        blank=True,
        null=True
    )

    active = models.BooleanField(default=True)

    is_special = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def has_started(self):
        """Return whether the event's scheduled start time has passed."""

        event_start = datetime.combine(
            self.date,
            self.time,
        )

        now = timezone.now()

        if timezone.is_aware(now):
            event_start = timezone.make_aware(
                event_start,
                timezone.get_current_timezone(),
            )

        return now >= event_start

    @property
    def places_booked(self):
        """Return the number of currently booked places."""

        return sum(
            booking.quantity
            for booking in self.bookings.filter(status='confirmed')
        )

    @property
    def places_remaining(self):
        """Return the number of places still available."""

        return self.capacity - self.places_booked

    class Meta:
        ordering = ['date', 'time']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__gt=0),
                name='event_price_gt_0',
            ),
        ]

    def __str__(self):
        return self.name


class Booking(models.Model):
    """A user's booking for an event."""

    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings'
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.PROTECT,
        related_name='bookings'
    )

    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
    )

    total_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )

    stripe_session_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='confirmed'
    )

    stripe_refund_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    cancelled_at = models.DateTimeField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity__gte=1),
                name='booking_quantity_gte_1',
            ),
        ]

    @property
    def total_price(self):
        """Return the amount originally paid for this booking."""

        if self.total_paid is not None:
            return self.total_paid

        return self.event.price * self.quantity

    @property
    def price_per_place(self):
        """Return the original price paid per place."""

        if self.total_paid is not None and self.quantity:
            return self.total_paid / self.quantity

        return self.event.price

    def __str__(self):
        return f"{self.user.username} - {self.event.name}"
