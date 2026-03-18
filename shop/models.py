from django.db import models
from django.contrib.auth.models import User

class Pet(models.Model):
    name = models.CharField(max_length=120)
    species = models.CharField(max_length=50, blank=True)
    age = models.CharField(max_length=50, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.species})"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    items_snapshot = models.TextField()
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.id} by {self.user.username} - {self.created_at.date()}"
