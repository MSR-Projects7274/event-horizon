from django.db import models
from django.contrib.auth.models import User


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
        """Return the number of places currently booked."""

        return sum(
            booking.quantity
            for booking in self.bookings.all()
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

    quantity = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.event.name}"
