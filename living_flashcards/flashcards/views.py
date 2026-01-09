from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from flashcards.models import Deck, CardInfo, CardToUser
from django.utils import timezone
from django.views.decorators.http import require_POST

# for fsrs
from fsrs import Scheduler, Card, Rating, ReviewLog
from datetime import datetime

# Create your views here.

scheduler = Scheduler()

# display correct cards
def flashcards(request, slug):
  # take slug and use to get deck to pass to template
  deck = get_object_or_404(Deck, name=slug)

  # Copilot code to create cardtouser instances any unseen cards
  existing_cards = CardToUser.objects.filter(card_id__deck=deck, user_id=request.user).values_list('card_id', flat=True)
  new_cards = deck.cards.exclude(id__in=existing_cards)
  
  for card_info in new_cards:
    CardToUser.objects.create(card_id=card_info, user_id=request.user)
  
  # end copilot

  to_review = get_cards_to_review(request, deck)

  start_card = to_review.first()

  # add some sort of error saying card couldn't be found/deck couldn't be found if its the case
  return render(request, 'flashcards.html', {'deck_info': deck, 'card': start_card})

def get_cards_to_review(request, deck): 
  now = timezone.now()
  # all cardtouser cards for current user, code written by Copilot
  user_cards = CardToUser.objects.filter(card_id__deck=deck, user_id=request.user)
  # sorted by review time, lte = less than or equal to, gets cards whose next review date is in the past
  to_review = (user_cards.filter(see_next__lte=now) | user_cards.filter(see_next__isnull=True)).order_by('see_next')
  return (to_review)

# takes input from HTML form
# updates current card's stats and moves on to next one
@require_POST
def review_card(request): 
  user_confidence_rating = request.POST.get("rating")
  card_id = request.POST.get("card_id")
  # tbh idk why i have this here its just what came to mind
  assert user_confidence_rating in ["easy", "good", "hard", "again"]
  # need to get the current card on display
  card = get_object_or_404(CardToUser, card_id__card_id=card_id, user_id=request.user.id)
  # now update next reviews for card + spacing
  review_card = card.get_card() # creates fsrs card object w/ data

  if user_confidence_rating == "easy": 
    rating = Rating.Easy
  elif user_confidence_rating == "good": 
    rating = Rating.Good
  elif user_confidence_rating == "hard": 
    rating = Rating.Hard
  else: 
    rating = Rating.Again

  updated_card, review_log = scheduler.review_card(review_card, rating)
  # save new card data
  card.update_json(updated_card)
  card.save()

  deck = get_object_or_404(CardInfo, card_id=card_id).deck

  # re-load cards to review
  to_review = get_cards_to_review(request, deck)

  start_card = to_review.first()

  return render(request, 'flashcards.html', {'deck_info': deck, 'card': start_card})