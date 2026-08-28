from django.urls import path

from . import views

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('<int:event_id>/', views.event_detail, name='event_detail'),
    path('<int:event_id>/book/', views.book_event, name='book_event'),
    path('booking/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
]