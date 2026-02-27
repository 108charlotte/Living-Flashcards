from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from .models import UserLanguage

# Create your views here.
def langselection(request): 
    return render(request, 'lang_selection.html', {'available_languages': ['English']})

@require_POST
def setlanguage(request): 
    if request.user.is_authenticated: 
        language = request.POST.get('language', 'en')
        UserLanguage.objects.update_or_create(djangousermodel=request.user, defaults={'language': language})

    return redirect('all_decks:all_decks')