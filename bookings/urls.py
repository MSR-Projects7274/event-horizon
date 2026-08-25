from django.urls import path

from . import views
from .webhook import stripe_webhook


urlpatterns = [
    path('checkout/<int:event_id>/', views.create_checkout_session, name='create_checkout_session',),
    path('wh/',stripe_webhook, name='stripe_webhook',),
    path('success/', views.booking_success, name='booking_success',),
]