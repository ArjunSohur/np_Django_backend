from django.contrib import admin
from .models import SubjectVector, NewsArticle, PickledUser, ArticleRating

admin.site.register(SubjectVector)
admin.site.register(NewsArticle)
admin.site.register(PickledUser)
admin.site.register(ArticleRating)


