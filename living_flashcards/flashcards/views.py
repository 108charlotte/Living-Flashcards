from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader


# Create your views here.

def flashcards(request):
  template = loader.get_template('flashcards.html')
  return HttpResponse(template.render())