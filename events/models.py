from django.contrib.auth.models import User
from django.db import models


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
        on_delete=models.CASCADE,
        related_name='events'
    )

    name = models.CharField(max_length=200)

    description = models.TextField()

    location = models.CharField(max_length=255)

    date = models.DateField()

    time = models.TimeField()

    price = models.DecimalField(
        max_digits=8,
        decimal_places=2
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
        on_delete=models.CASCADE,
        related_name='bookings'
    )

    quantity = models.PositiveIntegerField(
        default=1
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

    @property
    def total_price(self):
        """Return the total price for this booking."""

        return self.event.price * self.quantity

    def __str__(self):
        return f"{self.user.username} - {self.event.name}"
