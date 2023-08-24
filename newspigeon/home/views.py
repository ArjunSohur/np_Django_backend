from typing import Any, Dict
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import SubjectVector, NewsArticle
from prefs.models import CategoryRating
from django.views.generic import ListView
from user_nn_logic.dynamic_handler import DynamicHandler
import json

initialPreferences = [
    [
        ["Business", 5],
        ["Finance", 5],
        ["Economics", 5],
        ["Startup", 5],
    ],
    [
        ["Science", 5],
        ["Computer Science", 5],
        ["Artificial Intelligence", 5],
        ["Technology", 5],
        ["Medical Research", 5],
        ["Pharmaceutical", 5],
    ],
    [
        ["Entertainment", 5],
        ["Weather", 5],
        ["Art", 5],
        ["Health", 5],
        ["Lifestyle", 5],
        ["Celebrity", 5],
        ["Fashion and Beauty", 5],
        ["Travel", 5],
    ],
    [
        ["Politics", 5],
        ["US Politics", 5],
        ["UK Politics", 5],
        ["European Politics", 5],
        ["Canadian Politics", 5],
        ["South America", 5],
        ["World", 5],
        ["Middle East", 5],
        ["Africa", 5],
        ["China", 5],
        ["Asia", 5],
    ],
    [
        ["Sports", 5],
        ["Soccer/Football", 5],
        ["American Football", 5],
        ["Basketball", 5],
        ["Hockey", 5],
        ["Baseball", 5],
        ["Tennis", 5],
        ["Rugby", 5],
        ["Cricket", 5]
    ]
]

initialCategoryRatings = [
    ["Business, Finance, and Economics", 5],
    ["Science and Technology", 5],
    ["Entertainment, Art, and Health", 5],
    ["Domestic and World Politics", 5],
    ["Sports", 5]

]

initialUnusedTopics = [[], [], [], [], []]

@login_required
def home(request):
    return render(request, "home/home.html")

def parseCategoryRatings(large_cat_ratings):
    cat_ratings, prefs = []

    for i in range(len(large_cat_ratings)):
        for j in range(len(large_cat_ratings[i])):
            if j == 0: 
                cat_ratings.append(large_cat_ratings[i][j])
            elif j == 1:
                prefs.append(large_cat_ratings[i][j])
    
    return prefs, cat_ratings

def getratings(user):
    user_prefs, created = CategoryRating.objects.get_or_create(user=user)

    if created:
        # Initialize with hardcoded preferences for new users
        full_ratings = []
        for i in range(len(initialCategoryRatings)):
            temp_ratings = []
            temp_ratings.append(initialCategoryRatings[i])
            temp_ratings.append(initialPreferences[i])
            temp_ratings.append(initialUnusedTopics[i])

            full_ratings.append(temp_ratings)

        user_prefs.category_ratings_json = json.dumps(full_ratings)
        user_prefs.save()
    
    subject_vectors = SubjectVector.objects.all()

    preferences, short_category_ratings = parseCategoryRatings(CategoryRating.objects.get_or_create(user=user))

    return preferences, short_category_ratings, subject_vectors



class HomeListView(ListView):
    # Initialize ------------------------------------------------------------------------------
    handler = DynamicHandler()

    user = ListView.request.user

    preferences, short_category_ratings, subject_vectors = getratings(user=user)
    

    handler.initialize_context(preferences=preferences, category_ratings=short_category_ratings,
                                subject_vectors=subject_vectors, user_bias=5)
    
    # ------------------------------------------------------------------------------------------
    
    def get_context_data(self, **kwargs):
        user = self.request.user
        preferences, short_category_ratings, subject_vectors = getratings(user=user)

        self.handler.update_attributes(preferences=preferences, category_ratings=short_category_ratings, subject_vectors=subject_vectors)

        articles = NewsArticle.objects.all()

        recs = self.handler.get_recommendations(articles=articles)

        return recs
    
    def process_rating(self, article, rating):
        self.handler.handle_feedback(article=article, rating=rating)






