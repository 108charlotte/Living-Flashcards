from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.conf import settings
from flashcards.models import Deck

# Create your views here.

def all_decks(request):
  decks = Deck.objects.all()
  return render(request, 'all_decks.html', {'decks': decks})