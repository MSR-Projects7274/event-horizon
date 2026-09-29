from django.contrib import admin

from .models import CheckoutResolution


@admin.register(CheckoutResolution)
class CheckoutResolutionAdmin(admin.ModelAdmin):
    """Read-only audit view for unfulfilled paid Checkout sessions."""

    list_display = (
        'stripe_session_id',
        'user',
        'event',
        'reason',
        'refund_status',
        'created_at',
        'updated_at',
    )

    list_filter = (
        'reason',
        'refund_status',
        'created_at',
    )

    search_fields = (
        'stripe_session_id',
        'stripe_refund_id',
        'user__username',
        'user__email',
        'event__name',
    )

    readonly_fields = (
        'user',
        'event',
        'stripe_session_id',
        'stripe_refund_id',
        'reason',
        'refund_status',
        'created_at',
        'updated_at',
    )

    ordering = ('-created_at',)

    def has_add_permission(self, request):
        """Prevent audit records being created manually in Django Admin."""
        return False

    def has_change_permission(self, request, obj=None):
        """Keep payment-resolution audit records read-only."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Preserve payment-resolution audit history."""
        return False
