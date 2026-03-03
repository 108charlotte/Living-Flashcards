from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader
# Copilot generated: import Review model to record per-review events
from flashcards.models import Deck, CardInfo, CardToUser, Review
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
  deck = get_object_or_404(Deck, slug=slug)

  # Copilot code to create cardtouser instances any unseen cards
  existing_cards = CardToUser.objects.filter(card_id__deck=deck, user_id=request.user).values_list('card_id', flat=True)
  new_cards = deck.cards.exclude(id__in=existing_cards)
  
  for card_info in new_cards:
    CardToUser.objects.create(card_id=card_info, user_id=request.user)
  
  # end copilot

  to_review = get_cards_to_review(request, deck)

  start_card = to_review.first()

  if start_card: 
    review_intervals = get_review_intervals(start_card)

  # need to add some sort of error saying card couldn't be found/deck couldn't be found if its the case
  return render(request, 'flashcards.html', {'deck_info': deck, 'card': start_card, 'review_intervals': review_intervals})

def get_cards_to_review(request, deck): 
  now = timezone.now()
  # all cardtouser cards for current user, code written by Copilot
  user_cards = CardToUser.objects.filter(card_id__deck=deck, user_id=request.user)
  # sorted by review time, lte = less than or equal to, gets cards whose next review date is in the past
  to_review = (user_cards.filter(see_next__lte=now) | user_cards.filter(see_next__isnull=True)).order_by('see_next')
  return (to_review)

def clean_times(now, due_date): 
  difference = due_date - now

  mins = int(difference.total_seconds() / 60)
  hours = int(difference.total_seconds() / 3600)
  days = difference.days

  # definitely need to clean this up
  if mins < 10: 
    return "< 10 mins"
  elif mins < 15: 
    return "< 15 mins"
  elif mins < 20: 
    return "< 20 mins"
  elif mins < 30: 
    return "< 30 mins"
  elif hours < 1: 
    return "< 1 hr"
  elif hours < 2: 
    return "< 2 hrs"
  elif hours < 24: 
    return f"{hours} hrs"
  else: 
    return f"{days} days"


def get_review_intervals(card_to_user): 
  card = card_to_user.get_card()

  now = timezone.now()

  # Claude code which simulates reviewing with each rating to get the resulting cards
  again_card, _ = scheduler.review_card(card, Rating.Again, now)
  hard_card, _ = scheduler.review_card(card, Rating.Hard, now)
  good_card, _ = scheduler.review_card(card, Rating.Good, now)
  easy_card, _ = scheduler.review_card(card, Rating.Easy, now)

  # Claude code to get review intervals based on user selection
  review_intervals = {
    'again': clean_times(now, again_card.due),
    'hard': clean_times(now, hard_card.due),
    'good': clean_times(now, good_card.due),
    'easy': clean_times(now, easy_card.due),
  }

  return review_intervals

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

  # Copilot generated: record the review event (do not break review flow on failure)
  try:
    # Save textual rating if available
    rating_str = None
    if rating == Rating.Easy:
        rating_str = 'easy'
    elif rating == Rating.Good:
        rating_str = 'good'
    elif rating == Rating.Hard:
        rating_str = 'hard'
    elif rating == Rating.Again:
        rating_str = 'again'

    Review.objects.create(user=request.user, card=card.card_id, rating=rating_str)
  except Exception:
    # Do not fail the review flow if analytics recording fails
    pass

  deck = get_object_or_404(CardInfo, card_id=card_id).deck

  # re-load cards to review
  to_review = get_cards_to_review(request, deck)

  start_card = to_review.first()

  if start_card: 
    review_intervals = get_review_intervals(start_card)
  else: 
    review_intervals = [None, None, None, None]

  return render(request, 'flashcards.html', {'deck_info': deck, 'card': start_card, 'review_intervals': review_intervals})