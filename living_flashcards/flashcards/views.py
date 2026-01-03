from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from flashcards.models import Deck, CardInfo, CardToUser
from django.utils import timezone
from django.views.decorators.http import require_POST

# for fsrs
from fsrs import Scheduler, Card, Rating, ReviewLog
from datetime import datetime, timezone

# Create your views here.

scheduler = Scheduler()

# display correct cards
def flashcards(request, slug):
  template = loader.get_template('flashcards.html')
  # take slug and use to get deck to pass to template
  deck = get_object_or_404(Deck, name=slug)
  now = timezone.now()

  # all cardtouser cards for current user, code written by Copilot
  user_cards = CardToUser.objects.filter(card_id__deck=deck, user_id=request.user)
  # lte = less than or equal to, gets cards whose next review date is in the past
  to_review = user_cards.filter(see_next__lte=now).order_by('see_next')

  start_card = to_review.first()
  # add some sort of error saying deck couldn't be found
  return render(request, 'flashcards.html', {'deck_info': deck, 'to_review': to_review, 'card_id': start_card.card_id.card_id})


# takes input from HTML form
# updates current card's stats and moves on to next one
@require_POST
def review_card(request): 
  user_confidence_rating = request.POST.get("rating")
  card_id = request.POST.get("card_id")
  # tbh idk why i have this here its just what came to mind
  assert user_confidence_rating in ["easy", "good", "hard", "again"]
  # need to get the current card on display
  card = get_object_or_404(CardToUser, card_id=card_id, user_id=request.user.id)
  # now update next reviews for card + spacing
  review_card = card.review_card

  if user_confidence_rating == "easy": 
    rating = Rating.Easy
  if user_confidence_rating == "good": 
    rating = Rating.Good
  if user_confidence_rating == "hard": 
    rating = Rating.Hard
  else: 
    rating = Rating.Again

  scheduler.review_card(review_card, rating)
  



"""
from fsrs import Scheduler, Card, Rating, ReviewLog
from datetime import datetime, timezone

scheduler = Scheduler()

card = Card()

rating = Rating.Good

card, review_log = scheduler.review_card(card, rating)

due = card.due

time_delta = due - datetime.now(timezone.utc)
"""