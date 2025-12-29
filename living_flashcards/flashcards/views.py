from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.conf import settings
from flashcards.models import Deck, Card
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.db.models import Q

# Create your views here.

# display correct cards
def flashcards(request, slug):
  template = loader.get_template('flashcards.html')
  # take slug and use to get deck to pass to template
  deck = get_object_or_404(Deck, name=slug)
  now = timezone.now()
  # lte = less than or equal to, gets cards whose next review date is in the past
  to_review = deck.cards.filter(see_next__lte=now).order_by('see_next')
  new = deck.cards.filter(see_next__isnull=True)
  # union operator, will combine
  combined_cards = to_review | new
  start_card = combined_cards.first()
  # add some sort of error saying deck couldn't be found
  return render(request, 'flashcards.html', {'deck_info': deck, 'to_review': to_review, 'new': new, 'card_id': start_card.card_id})

@require_POST

# takes input from HTML form
# updates current card's stats and moves on to next one
@require_POST
def review_card(request): 
  user_confidence_rating = request.POST.get("rating")
  card_id = request.POST.get("card_id")
  # tbh idk why i have this here its just what came to mind
  assert user_confidence_rating in ["easy", "good", "hard", "again"]
  # need to get the current card on display
  card = get_object_or_404(Card, card_id=card_id)
  # now update next reviews for card + spacing