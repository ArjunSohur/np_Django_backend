from django.contrib import admin
from .models import SubjectVector, NewsArticle, PickledUser

admin.site.register(SubjectVector)
admin.site.register(NewsArticle)
admin.site.register(PickledUser)

