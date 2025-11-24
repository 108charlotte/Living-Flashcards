from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

# Create your views here.

def all_decks(request):
  template = loader.get_template('all_decks.html')
  # replace with code to actually populate flashcards from .csv or API
  deck_names = {"category1": {"cat": "idk", "dog": "idk"}, "category2": {"no": "yes"}}
  return render(request, 'all_decks.html', {'flashcard_data': terms_and_definitions})