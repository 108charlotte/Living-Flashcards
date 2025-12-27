from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.conf import settings
from flashcards.models import Deck
from django.utils import timezone

# Create your views here.

def flashcards(request, slug):
  template = loader.get_template('flashcards.html')
  # take slug and use to get deck to pass to template
  deck = get_object_or_404(Deck, name=slug)
  now = timezone.now()
  # lte = less than or equal to, gets cards whose next review date is in the past
  to_review = deck.cards.filter(see_next__lte=now).order_by('see_next')
  new = deck.cards.filter(see_next__isnull=True)
  # add some sort of error saying deck couldn't be found
  return render(request, 'flashcards.html', {'deck_info': deck, 'to_review': to_review, 'new': new})