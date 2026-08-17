from django.contrib import admin
from .models import Category, Event


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'date',
        'time',
        'price',
        'capacity',
        'active',
        'is_special',
    )

    list_filter = (
        'category',
        'active',
        'is_special',
        'date',
    )

    search_fields = (
        'name',
        'description',
        'location',
    )

    ordering = ('date', 'time')