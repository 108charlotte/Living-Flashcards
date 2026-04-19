from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader
# Copilot generated: import Review model to record per-review events
from flashcards.models import Deck, CardInfo, CardToUser, Review
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from authentication.models import UserStudySettings
import math

# for fsrs
from fsrs import Scheduler, Card, Rating, ReviewLog
from datetime import datetime

# Estimated Time to complete deck--mostly copilot generated, with various edits and clean up by me. 
def estimate_deck_completion_time(request, deck):
    """
    Estimate how long it will take to complete reviewing all cards in a deck.

    Algorithm:
    - Base time per card: 8 seconds
    - Multiplier based on "again" interval: shorter intervals = harder cards = more time
    - Formula: multiplier = max(1, 4 / log(interval_minutes + 1))
    """
    BASE_TIME_PER_CARD = 8  # seconds
    BASE_MULTIPLIER = 4
    cards_to_review = get_cards_to_review(request.user, deck)
    total_seconds = 0
    reviewed_card_ids = set()
    for card_to_user in cards_to_review:
        fsrs_card = card_to_user.get_card()
        now = timezone.now()
        again_card, _ = scheduler.review_card(fsrs_card, Rating.Again, now)
        interval_seconds = (again_card.due - now).total_seconds()
        interval_minutes = max(1, interval_seconds / 60)
        multiplier = max(1, BASE_MULTIPLIER / math.log(interval_minutes + 1))
        card_time = BASE_TIME_PER_CARD * multiplier
        total_seconds += card_time
        reviewed_card_ids.add(card_to_user.card_id.id)
    # Add unseen cards (no CardToUser row for this user)
    user_cards = CardToUser.objects.filter(card_id__deck=deck, user_id=request.user)
    seen_card_ids = set(user_cards.values_list('card_id', flat=True))
    all_card_ids = set(deck.cards.values_list('id', flat=True))
    unseen_card_ids = all_card_ids - seen_card_ids
    unseen_count = len(unseen_card_ids)
    if unseen_count > 0:
        total_seconds += unseen_count * BASE_TIME_PER_CARD
    total_minutes = math.ceil(total_seconds / 60)
    return total_minutes

# everything will redirect here instead of to deck_preview, and it will handle traffic depending on whether the user has ever reviewed a deck before
@login_required
def instructions_screen(request, slug): 
    user_model, _ = UserStudySettings.objects.get_or_create(user=request.user)
    if user_model.first_deck_opened is None:
      user_model.first_deck_opened = timezone.localdate()
      user_model.save()
      return render(request, 'first_time_instructions.html', {'deck_slug': slug})
    return deck_preview(request, slug)
   

# Deck preview view
from django.contrib.auth.decorators import login_required
@login_required
def deck_preview(request, slug):
    deck = get_object_or_404(Deck, slug=slug)
    user = request.user
    today = timezone.localdate()
    daily_new_limit = get_daily_new_limit(user)
    user_cards = CardToUser.objects.filter(card_id__deck=deck, user_id=user.id)
    reviewed_count = user_cards.exclude(review_card={}).count()
    introduced_today_count = user_cards.filter(new_introduced_on=today).count()
    remaining_budget = max(daily_new_limit - introduced_today_count, 0)
    previously_introduced_new_count = user_cards.filter(review_card={}).exclude(
        new_introduced_on__isnull=True
    ).count()
    not_yet_introduced_new_count = user_cards.filter(
        review_card={},
        new_introduced_on__isnull=True,
    ).count()
    unseen_new_count = max(deck.cards.count() - user_cards.count(), 0)
    introducible_new_count = not_yet_introduced_new_count + unseen_new_count
    new_count = previously_introduced_new_count + min(
        remaining_budget,
        introducible_new_count,
    )
    learning_count = reviewed_count
    estimated_time = estimate_deck_completion_time(request, deck)
    phonetic = getattr(deck, 'phonetic', '')
    total_cards = deck.cards.count()
    return render(request, 'deck_preview.html', {
        'deck': deck,
        'new_count': new_count,
        'learning_count': learning_count,
        'estimated_time': estimated_time,
        'phonetic': phonetic,
        'total_cards': total_cards,
    })

scheduler = Scheduler()

# Session keys used to persist progress state across POST submissions
# so the progress bar can be based on completed/(completed+remaining).
PROGRESS_DECK_SESSION_KEY = 'flashcards_progress_deck_id'
PROGRESS_COMPLETED_SESSION_KEY = 'flashcards_progress_completed'


def get_daily_new_limit(user):
  # Pull persisted user preference, creating defaults if missing.
  settings_obj, _ = UserStudySettings.objects.get_or_create(user=user)

  # Runtime clamp ensures safe behavior even if malformed data exists.
  return max(5, min(30, settings_obj.daily_new_limit))

# display correct cards
@login_required
def flashcards(request, slug):
  # take slug and use to get deck to pass to template
  deck = get_object_or_404(Deck, slug=slug)

  # Copilot code to create cardtouser instances any unseen cards
  existing_cards = CardToUser.objects.filter(card_id__deck=deck, user_id=request.user).values_list('card_id', flat=True)
  new_card = CardInfo.objects.filter(deck=deck).exclude(id__in=existing_cards).only('id').first()
  if new_card:
      CardToUser.objects.create(card_id=new_card, user_id=request.user) # create new cardtouser instance

  to_review = get_cards_to_review(request.user, deck)

  remaining_cards = to_review.count()

  start_card = to_review.first()

  if start_card:
    # Initialize progress state when a review run begins for this deck.
    # Progress fill should follow completed / (completed + remaining).
    request.session[PROGRESS_DECK_SESSION_KEY] = deck.id
    request.session[PROGRESS_COMPLETED_SESSION_KEY] = 0
    current_index = 0
    total_cards = remaining_cards
    review_intervals = get_review_intervals(start_card)
    estimated_time = estimate_deck_completion_time(request, deck)
  else:
    # No due cards means no visible progress in the bar.
    current_index = 0
    total_cards = 0
    review_intervals = [None, None, None, None]
    estimated_time = 0

  # need to add some sort of error saying card couldn't be found/deck couldn't be found if its the case
  return render(request, 'flashcards.html', {
    'deck_info': deck,
    'card': start_card,
    'review_intervals': review_intervals,
    'currentIndex': current_index,
    'totalCards': total_cards,
    'estimated_time': estimated_time,
    'hide_main_nav': True,
  })

def get_cards_available_to_review(user, deck):
    now = timezone.now()
    today = timezone.localdate()
    user_cards = CardToUser.objects.filter(card_id__deck=deck, user_id=user)
    daily_new_limit = get_daily_new_limit(user)
    
    learning_due = user_cards.exclude(review_card={}).filter(see_next__lte=now)
    previously_introduced_new = user_cards.filter(review_card={}, new_introduced_on__isnull=False)

    return (learning_due | previously_introduced_new)

# optimized by Copilot (making improvements to combat slow load time)
def count_cards_available_to_review(user, deck, user_cards=None):
    if user_cards is None:
        user_cards = CardToUser.objects.filter(card_id__deck=deck, user_id=user)
    now = timezone.now()
    learning_due = [c for c in user_cards if getattr(c, 'review_card', {}) != {} and getattr(c, 'see_next', None) is not None and c.see_next <= now]
    previously_introduced_new = [c for c in user_cards if getattr(c, 'review_card', {}) == {} and getattr(c, 'new_introduced_on', None) is not None]
    return len(learning_due) + len(previously_introduced_new)

def get_cards_to_review(user, deck): 
  # Learning cards are reviewed at least once and due now/past; they are never capped.
  learning_and_prev_new = get_cards_available_to_review(user, deck)

  today = timezone.localdate()
  user_cards = CardToUser.objects.filter(card_id__deck=deck, user_id=user)
  daily_new_limit = get_daily_new_limit(user)
  introduced_today_count = user_cards.filter(new_introduced_on=today).count()
  remaining_budget = max(daily_new_limit - introduced_today_count, 0)

  if remaining_budget > 0:
    # Copilot speed optimization: Only introduce one new card per review to minimize DB writes
    newly_introduced_id = (
      user_cards
      .filter(review_card={}, new_introduced_on__isnull=True)
      .order_by('id')
      .values_list('id', flat=True)
      .first()
    )
    if newly_introduced_id:
      user_cards.filter(id=newly_introduced_id).update(new_introduced_on=today)

  available_new_cards = user_cards.filter(review_card={}).exclude(new_introduced_on__isnull=True)

  # Combine learning+prev_new and available new cards into the queue shown to the user.
  to_review = (learning_and_prev_new | available_new_cards).order_by('see_next', 'id')
  return to_review


# uses code from get_cards_to_review and get_new_cards_for_today
def count_learning_cards(user, deck):
    now = timezone.now()
    user_cards = CardToUser.objects.filter(card_id__deck=deck, user_id=user.id)
    return user_cards.exclude(review_card={}).filter(see_next__lte=now).count()

# uses code from get_cards_to_review and get_new_cards_for_today and help from copilot
def count_new_cards_available_today(user, deck, user_cards=None):
    today = timezone.localdate()
    if user_cards is None:
        user_cards = CardToUser.objects.filter(card_id__deck=deck, user_id=user.id)
    daily_new_limit = get_daily_new_limit(user)
    introduced_today_count = sum(1 for c in user_cards if getattr(c, 'new_introduced_on', None) == today)
    remaining_budget = max(daily_new_limit - introduced_today_count, 0)
    not_yet_introduced = sum(1 for c in user_cards if getattr(c, 'review_card', {}) == {} and getattr(c, 'new_introduced_on', None) is None)
    seen_card_ids = set(getattr(c.card_id, 'id', None) for c in user_cards)
    all_card_ids = set(deck.cards.values_list('id', flat=True))
    unseen_count = len(all_card_ids - seen_card_ids)
    total_new = not_yet_introduced + unseen_count
    return min(total_new, remaining_budget)

def get_new_cards_for_today(user, deck): 
  today = timezone.localdate()
  # all cardtouser cards for current user, code written by Copilot
  user_cards = CardToUser.objects.filter(card_id__deck=deck, user_id=user)
  daily_new_limit = get_daily_new_limit(user)
  # Strict daily budget:
  # 1) Count how many cards were introduced today for this deck/user.
  # 2) Introduce only the remaining number of brand-new cards today.
  # 3) Always keep previously introduced-but-unreviewed new cards available.
  introduced_today_count = user_cards.filter(new_introduced_on=today).count()
  remaining_budget = max(daily_new_limit - introduced_today_count, 0)

  if remaining_budget > 0:
    newly_introduced_ids = list(
      user_cards
      .filter(review_card={}, new_introduced_on__isnull=True)
      .order_by('id')
      .values_list('id', flat=True)[:remaining_budget]
    )
    if newly_introduced_ids:
      user_cards.filter(id__in=newly_introduced_ids).update(new_introduced_on=today)

  available_new_cards = user_cards.filter(review_card={}).exclude(new_introduced_on__isnull=True)
  return available_new_cards


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
@login_required
@require_POST
def review_card(request): 
  user_confidence_rating = request.POST.get("rating")
  card_id = request.POST.get("card_id")
  # tbh idk why i have this here its just what came to mind
  assert user_confidence_rating in ["easy", "good", "hard", "again"]
  # need to get the current card on display
  card = get_object_or_404(CardToUser.objects.select_related('card_id'), card_id__card_id=card_id, user_id=request.user.id)
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

  deck = card.card_id.deck

  # re-load cards to review
  to_review = get_cards_to_review(request.user, deck)

  remaining_cards = to_review.count()

  start_card = to_review.first()

  saved_deck_id = request.session.get(PROGRESS_DECK_SESSION_KEY)
  saved_completed = request.session.get(PROGRESS_COMPLETED_SESSION_KEY)

  # If session progress is missing/stale (new deck or refreshed session),
  # rebuild baseline using "this review = 1 completed".
  if saved_deck_id != deck.pk or not isinstance(saved_completed, int):
    completed_cards = 1
  else:
    completed_cards = saved_completed + 1

  if completed_cards < 0:
    completed_cards = 0

  total_cards = completed_cards + remaining_cards

  request.session[PROGRESS_DECK_SESSION_KEY] = deck.pk
  request.session[PROGRESS_COMPLETED_SESSION_KEY] = completed_cards

  if start_card:
    current_index = completed_cards
    review_intervals = get_review_intervals(start_card)
    estimated_time = estimate_deck_completion_time(request, deck)
  else:
    # If the run is complete, denominator remains completed + remaining = completed.
    current_index = completed_cards
    review_intervals = [None, None, None, None]
    estimated_time = 0

  return render(request, 'flashcards.html', {
    'deck_info': deck,
    'card': start_card,
    'review_intervals': review_intervals,
    'currentIndex': current_index,
    'totalCards': total_cards,
    'estimated_time': estimated_time,
    'hide_main_nav': True,
  })