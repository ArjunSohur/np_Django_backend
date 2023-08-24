from django.db import models

class SubjectVector(models.Model):
    name = models.CharField(max_length=200)
    value = models.TextField()


