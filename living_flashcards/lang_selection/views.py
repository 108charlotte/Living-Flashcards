from django.shortcuts import redirect, render

# Create your views here.
def langselection(request): 
    return render(request, 'lang_selection.html', {'available_languages': ['English']})

def setlanguage(request): 
    if request.method == "POST": 
        # logic to set language for user model instance
        return redirect('all_decks')