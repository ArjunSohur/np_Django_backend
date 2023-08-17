from django.db import models
from django.contrib.auth.models import User

class UserPrefs(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferences_json = models.TextField()  
    category_ratings_json = models.TextField()  
    unused_topics_json = models.TextField()  

