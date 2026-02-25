from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth import login, logout, authenticate
from lang_selection.models import UserLanguage

# Create your views here.
def sign_up(request): 
    if request.method == 'POST': 
        form = RegisterForm(request.POST)
        if form.is_valid(): 
            user = form.save()
            UserLanguage.objects.create(djangousermodel=user, language='en')
            login(request, user)
            return redirect('lang_selection:langselection')
    else: 
        form = RegisterForm()
    
    return render(request, 'registration/sign_up.html', {"form": form})

# Copilot generated placeholder removed: ReviewLog was undefined here.