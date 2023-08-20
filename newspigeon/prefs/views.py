from django.shortcuts import render
import json
from .models import UserPrefs
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.shortcuts import render, redirect
from django.http import JsonResponse



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

initialUnusedTopics = []


@login_required
def update_preferences(request):
    if request.method == 'POST':
        user = request.user
        user_prefs = UserPrefs.objects.get(user=user)

        updated_preferences = request.POST.get('preferences')  # Get updated preferences from POST data

        # Update the preferences field
        user_prefs.preferences_json = updated_preferences
        user_prefs.save()

        return JsonResponse({'message': 'Preferences updated successfully'})

    return JsonResponse({'message': 'Invalid request method'})



class PrefListView(ListView):
    model = UserPrefs
    template_name = "prefs/home.html"
    context_object_name = "user_prefs"

    def get_queryset(self):
        user = self.request.user
        user_prefs, created = UserPrefs.objects.get_or_create(user=user)

        if created:
            # Initialize with hardcoded preferences for new users
            user_prefs.preferences_json = json.dumps(initialPreferences)
            user_prefs.category_ratings_json = json.dumps(initialCategoryRatings)
            user_prefs.unused_topics_json = json.dumps(initialUnusedTopics)
            user_prefs.save()

        return UserPrefs.objects.filter(user=user)  # Return the user's preferences

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_prefs_queryset = context["user_prefs"]

        print("User Preferences Queryset:", user_prefs_queryset)

        for user_prefs in user_prefs_queryset:
            print("User:", user_prefs.user)
            print("Preferences JSON:", user_prefs.preferences_json)
            print("Category Ratings JSON:", user_prefs.category_ratings_json)
            print("Unused Topics JSON:", user_prefs.unused_topics_json)

        return context