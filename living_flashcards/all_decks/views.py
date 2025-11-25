from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.conf import settings

# Create your views here.

def all_decks(request):
  return render(request, 'all_decks.html', {'decks': settings.DECKS})