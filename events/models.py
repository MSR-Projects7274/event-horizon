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

    class Meta:
        ordering = ['date', 'time']

    def __str__(self):
        return self.name