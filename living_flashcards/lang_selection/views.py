from django.shortcuts import redirect, render
from .models import UserLanguage

# Create your views here.
def langselection(request): 
    return render(request, 'lang_selection.html', {'available_languages': ['English']})

def setlanguage(request): 
    if request.method == "POST": 
        if request.user.is_authenticated: 
            language = request.POST.get('user-language', 'en')
            UserLanguage.objects.update_or_create(djangousermodel=request.user, defaults={'language': language})

        return redirect('all_decks:all_decks')