from django.shortcuts import render
import json
from .models import CategoryRating
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.shortcuts import render
from user_nn_logic.user_class import User
from home.models import PickledUser, SubjectVector
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

def updateUserObject(request): 
    if request.method == 'POST':
        user = request.user

        rating_data = json.loads(request.body)

        cat_ratings = []
        prefs = []

        for i in range(len(rating_data)):
            for j in range(len(rating_data[i])):
                if j == 0: 
                    cat_ratings.append(rating_data[i][j])
                elif j == 1:
                    prefs.append(rating_data[i][j])
        
        subject_vectors = SubjectVector.objects.all()

        updated_user = User(preferences=prefs, category_ratings=cat_ratings, subject_vectors=subject_vectors, bias=5)

        print("new user ------------------------")
        print(updated_user.get_prefs())
        print("---------------------------------")

        pickled_updated_user = pickle.dumps(updated_user)

        old_pickled_data = PickledUser.objects.get(user=user)
        old_pickled_data.pickled_data = pickled_updated_user

        old_pickled_data.save()

        return JsonResponse({'message': 'PU updated and saved successfully.'})

    return JsonResponse({'message': 'PU failed.'}, status=400)




@login_required
def update_category_ratings(request):
    if request.method == 'POST':
        user = request.user
        data = json.loads(request.body)

        # Update the user's category_ratings_json field with the new data
        user_prefs = CategoryRating.objects.get(user=user)
        user_prefs.category_ratings_json = json.dumps(data)
        user_prefs.save()

        return JsonResponse({'message': 'Category ratings updated and saved successfully.'})

    return JsonResponse({'message': 'Invalid request method.'}, status=400)


class PrefListView(ListView):
    model = CategoryRating
    template_name = "prefs/home.html"
    context_object_name = "user_prefs"

    def get_queryset(self):
        user = self.request.user
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

        # Return the user's preferences
        return CategoryRating.objects.filter(user=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_prefs_queryset = context["user_prefs"]

        # Retrieve the first object from the queryset
        first_user_prefs = user_prefs_queryset.first()

        # Parse the JSON data from the first object
        category_ratings_data = json.loads(
            first_user_prefs.category_ratings_json)

        context["category_ratings"] = category_ratings_data

        return context