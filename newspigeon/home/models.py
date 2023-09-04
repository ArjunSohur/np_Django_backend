from django.db import models
from django.core.validators import MaxValueValidator
import pickle
from django.contrib.auth.models import User


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
    ratings = models.ManyToManyField(User, through='ArticleRating')

class ArticleRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=zip(range(1, 11), range(1, 11)))
    date = models.DateTimeField(auto_now_add=True, blank=True)


class PickledUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pickled_data = models.BinaryField()

    @classmethod
    def create_from_user(cls, user_instance):
        pickled_data = pickle.dumps(user_instance)
        return cls.objects.create(pickled_data=pickled_data)

    def get_user(self):
        return pickle.loads(self.pickled_data)
    
class nlp_models(models.Model):
    model = models.BinaryField()
    tokenizer = models.BinaryField()
    sentence_embedder = models.BinaryField()