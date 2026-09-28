from django.conf import settings
from django.db import models


class CheckoutResolution(models.Model):
    """Store the outcome of a paid Checkout that cannot become a booking."""

    REASON_CHOICES = [
        ('missing_user', 'Booking user unavailable'),
        ('unavailable_event', 'Event unavailable'),
        ('started_event', 'Event already started'),
    ]

    REFUND_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('requires_action', 'Requires action'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('canceled', 'Canceled'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='checkout_resolutions',
        null=True,
        blank=True,
    )

    event = models.ForeignKey(
        'events.Event',
        on_delete=models.SET_NULL,
        related_name='checkout_resolutions',
        null=True,
        blank=True,
    )

    stripe_session_id = models.CharField(
        max_length=255,
        unique=True,
    )

    stripe_refund_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
    )

    reason = models.CharField(
        max_length=30,
        choices=REASON_CHOICES,
    )

    refund_status = models.CharField(
        max_length=20,
        choices=REFUND_STATUS_CHOICES,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.stripe_session_id
