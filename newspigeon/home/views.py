from typing import Any, Dict
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import SubjectVector, NewsArticle, PickledUser
from prefs.models import CategoryRating
from django.views.generic import ListView
from user_nn_logic.user_class import User
import json
import pickle

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
    cat_ratings = []
    prefs = []

    rating_data = json.loads(large_cat_ratings.category_ratings_json)

    for i in range(len(rating_data)):
        for j in range(len(rating_data[i])):
            if j == 0: 
                cat_ratings.append(rating_data[i][j])
            elif j == 1:
                prefs.append(rating_data[i][j])
    
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

    preferences, short_category_ratings = parseCategoryRatings(CategoryRating.objects.get(user=user))

    return preferences, short_category_ratings, subject_vectors



class HomeListView(ListView):
    model = NewsArticle  # Specify the model to use
    template_name = 'home/home.html'  # Specify the template name
    context_object_name = 'articles'  # Specify the context variable name for the list of articles


    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        
        # Access the authenticated user using self.request.user
        self.user = self.request.user
        
        try:
            pickled_user = PickledUser.objects.get(user=self.user)
        except PickledUser.DoesNotExist:
            # User not found, create a PickledUser instance
            preferences, short_category_ratings, subject_vectors = getratings(user=self.user)
            
            new_user = User(preferences=preferences, category_ratings=short_category_ratings, subject_vectors=subject_vectors, bias=5)
            pickled_data = pickle.dumps(new_user)
            PickledUser.objects.create(user=self.user, pickled_data=pickled_data)
        
    def get_context_data(self, **kwargs):
        articles = NewsArticle.objects.all()
        pickled_user = PickledUser.objects.get(user=self.user).get_user()

        print(pickled_user)

        recs = pickled_user.get_recs(articles=articles)

        return {'recs': recs}
    
    def process_rating(self, article, rating):
        self.current_user.process_rating(article=article, rating=rating)

