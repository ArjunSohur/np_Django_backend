from django.db import models
from django.contrib.auth.models import User

class CategoryRating(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    category_ratings_json = models.TextField()

