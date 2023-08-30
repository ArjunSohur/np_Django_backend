from django.db import models

class nlp_models(models.Model):
    model = models.BinaryField()
    tokenizer = models.BinaryField()
    sentence_embedder = models.BinaryField()
