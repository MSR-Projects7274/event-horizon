from django.urls import path

from . import views


urlpatterns = [
    path('register/', views.register, name='register'),
    path('', views.profile, name='profile'),
    path('edit/', views.edit_profile, name='edit_profile'),
]