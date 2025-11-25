from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.conf import settings

# Create your views here.

def flashcards(request, slug):
  template = loader.get_template('flashcards.html')
  # take slug and use to get deck to pass
  decks = settings.DECKS
  deck_info = {}
  for deck in decks: 
    if deck["name"] == slug: 
      deck_info = deck
  # add some sort of error saying deck couldn't be found
  return render(request, 'flashcards.html', {'deck_info': deck_info})