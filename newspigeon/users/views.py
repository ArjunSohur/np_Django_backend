from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .forms import UserRegisterForm


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("email")
            messages.success(request, f"Account created for {email}")
            return redirect("home-home")
    else:
        form = UserRegisterForm()

    return render(request, "users/register.html", {"form": form})

@login_required
def profile(request):
    return render (request, "users/profile.html")
