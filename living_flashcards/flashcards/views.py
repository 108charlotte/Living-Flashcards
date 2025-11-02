from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader


# Create your views here.

def flashcards(request):
  template = loader.get_template('flashcards.html')
  # replace with code to actually populate flashcards from .csv or API
  terms_and_definitions = {"cat": "idk", "dog": "idk 2"}
  return render(request, 'flashcards.html', {'flashcard_data': terms_and_definitions})