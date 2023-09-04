from typing import Any, Dict
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import SubjectVector, NewsArticle, PickledUser, ArticleRating
from prefs.models import CategoryRating
from django.views.generic import ListView
from user_nn_logic.user_class import User
import json
import pickle
from decimal import Decimal, ROUND_HALF_UP

from .tasks import fetch_articles


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


def update_category_ratings(new_prefs, new_category_ratings, user):
    user_in_question = CategoryRating.objects.get(user=user)
    user_prefs = json.loads(user_in_question.category_ratings_json)

    copy_prefs = user_prefs

    for i in range(len(copy_prefs)):
        for j in range(len(copy_prefs[i])):
            if j == 0:
                copy_prefs[i][j][1] = float(max(1, min(10, Decimal(new_category_ratings[i][1]).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))))
            if j == 1:
                for k in range(len(copy_prefs[i][j])):
                    copy_prefs[i][j][k][1] = float(max(1, min(10, Decimal(new_prefs[i][k][1]).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))))

    
    user_in_question.category_ratings_json = json.dumps(copy_prefs)
    user_in_question.save()

@login_required
def process_rating(request):
    if request.method == 'POST':

        article_title = request.POST.get('article_title')    

        article = NewsArticle.objects.get(title=article_title)

        pickled_user = PickledUser.objects.get(user=request.user).get_user()

        rating = int(request.POST.get('rating'))

        pickled_user.process_rating( article_info=article, rating=rating)

        new_prefs, new_cat_ratings = pickled_user.get_prefs()

        update_category_ratings(new_prefs=new_prefs, new_category_ratings=new_cat_ratings, user=request.user)

        # Update or create the rating in the database
        ArticleRating.objects.update_or_create(
            user=request.user,
            article=article,
            defaults={'rating': rating}
        )

    return redirect("home-home")

def get_user_ratings(user, articles):
    user_ratings = ArticleRating.objects.filter(user=user, article__in=articles).values('article', 'rating')
    user_rating_dict = {rating['article']: rating['rating'] for rating in user_ratings}
    return user_rating_dict



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

        recs = pickled_user.get_recs(articles=articles)
        user_ratings = get_user_ratings(user=self.user, articles=articles)

        return {'recs': recs, 'user_ratings': user_ratings}
    
# -----------------------------------------------------------------------------------------------------------
def fetch_articles_view():
    fetch_articles.delay()


