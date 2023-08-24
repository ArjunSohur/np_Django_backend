from django.db import models

class SubjectVector(models.Model):
    name = models.CharField(max_length=200)
    value = models.TextField()

class NewsArticle(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()
    url = models.URLField()
    date = models.CharField(max_length=100)
    authors =  models.TextField()
    domain = models.URLField()
    vector =  models.TextField()

