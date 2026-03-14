from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.conf import settings
from flashcards.models import Deck
from django.utils import timezone
# Copilot generated: import Review for heatmap aggregation
from flashcards.models import CardToUser, Review
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.http import Http404
import json

# Create your views here.


def _get_deck_page_context(user):
    # Convert to list so we can keep a stable, explicit ordering while splitting decks.
    decks = list(Deck.objects.all())

    started_decks = []
    not_started_decks = []

    if user.is_authenticated:
        now = timezone.now()

        # Rule for seperating started and not-startedd decks:
        # A deck is "started" only if the user has at least one persisted Review event for any card inside that deck.
        started_deck_ids = set(
            Review.objects.filter(user=user)
            .values_list('card__deck_id', flat=True)
            .distinct()
        )

        for deck in decks:
            user_cards = CardToUser.objects.filter(card_id__deck=deck, user_id=user.id)
            if user_cards.exists():
                to_review = (user_cards.filter(see_next__lte=now) | user_cards.filter(see_next__isnull=True))
                deck.cards_to_review = to_review.count() # sets temp python attribute
            else:
                deck.cards_to_review = deck.cards.count()

            # Preserve original deck order while routing each deck into one section.
            if deck.id in started_deck_ids:
                started_decks.append(deck)
            else:
                not_started_decks.append(deck)
    else:
        for deck in decks:
            deck.cards_to_review = 0

    return {
        'decks': decks,
        'started_decks': started_decks,
        'not_started_decks': not_started_decks,
        'available_languages': ["English"],
        'available_languages_to_learn': ["Sora", "Future language 1", "Future language 2"],
    }

def all_decks(request):
    return render(request, 'all_decks.html', _get_deck_page_context(request.user))


@login_required
def deck_category(request, category):
    context = _get_deck_page_context(request.user)

    if category == 'started':
        context.update(
            {
                'page_title': 'Started decks',
                'category_decks': context['started_decks'],
                'empty_message': "You haven't started any decks yet.",
            }
        )
    elif category == 'not-started':
        context.update(
            {
                'page_title': 'Not started yet',
                'category_decks': context['not_started_decks'],
                'empty_message': "You've started all available decks.",
            }
        )
    else:
        raise Http404('Deck category not found.')

    return render(request, 'deck_category.html', context)

def about(request):
    return render(request, "about.html")

def contact(request):
    return render(request, "contact.html")

# Copilot generated code to add a new API endpoint for fetching heatmap data
@login_required
def get_heatmap_data(request):
    """
    Fetch review statistics for heatmap visualization.
    Returns calendar data (reviews by day), due_calendar, streak, and daily_average.
    """
    from flashcards.models import CardToUser
    
    # Get all user's reviews
    user_cards = CardToUser.objects.filter(user_id=request.user)
    
    # Today's start in user's timezone
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_date_key = today_start.strftime('%Y-%m-%d')
    
    # ===== 1. PAST REVIEWS =====
    # (Copilot Generated) Prefer the new `Review` model history. Aggregate by local date string YYYY-MM-DD.
    reviews_by_day = {}
    try:
        user_reviews = Review.objects.filter(user=request.user).values_list('created_at', flat=True)
        for dt in user_reviews:
            local_date = timezone.localtime(dt).date().strftime('%Y-%m-%d')
            reviews_by_day[local_date] = reviews_by_day.get(local_date, 0) + 1
    except Exception:
        reviews_by_day = {}
    
    # ===== 2. TODAY'S REVIEW COUNT =====
    today_count = reviews_by_day.get(today_date_key, 0)
    reviews_by_day[today_date_key] = today_count
    
    # ===== 3. FUTURE DUE CARDS =====
    due_by_day = {}
    for card_to_user in user_cards:
        if card_to_user.see_next and card_to_user.see_next > timezone.now():
            due_date_key = card_to_user.see_next.date().strftime('%Y-%m-%d')
            due_by_day[due_date_key] = due_by_day.get(due_date_key, 0) + 1
    
    # ===== 4. STREAK CALCULATION =====
    streak = 0
    # Count consecutive days ending today that have reviews
    try:
        check_date = timezone.localdate()
        while True:
            key = check_date.strftime('%Y-%m-%d')
            if reviews_by_day.get(key, 0) > 0:
                streak += 1
                check_date = check_date - timedelta(days=1)
            else:
                break
    except Exception:
        streak = 0
    
    # ===== 5. DAILY AVERAGE =====
    # daily_average: total review events / days since first review (fallback to 1)
    try:
        total_reviews = sum(reviews_by_day.values())
        first_review = Review.objects.filter(user=request.user).order_by('created_at').first()
        if first_review:
            days_elapsed = (timezone.localdate() - timezone.localtime(first_review.created_at).date()).days + 1
            days_elapsed = max(days_elapsed, 1)
        else:
            days_elapsed = 1
        daily_average = total_reviews / days_elapsed if total_reviews > 0 else 0
    except Exception:
        daily_average = 0
    
    return JsonResponse({
        "calendar": reviews_by_day,
        "streak": streak,
        "due_calendar": due_by_day,
        "today_date_key": today_date_key,
        "daily_average": daily_average
    })