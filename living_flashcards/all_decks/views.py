from django.shortcuts import render, redirect
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
from django.views.decorators.http import require_POST
import json
from authentication.models import UserStudySettings
from authentication.forms import UserDailyLimitForm

# Create your views here.

STUDY_LANGUAGES = ["Sora", "Future Language 1", "Future Language 2"]
FUTURE_STUDY_LANGUAGES = {"Future Language 1", "Future Language 2"}


def get_daily_new_limit(user):
    # Use the persisted user preference and clamp to current allowed bounds.
    settings_obj, _ = UserStudySettings.objects.get_or_create(user=user)
    return max(5, min(30, settings_obj.daily_new_limit))


def _get_deck_page_context(user):
    # Convert to list so we can keep a stable, explicit ordering while splitting decks.
    decks = list(Deck.objects.all())

    started_decks = []
    not_started_decks = []

    if user.is_authenticated:
        today = timezone.localdate()
        daily_new_limit = get_daily_new_limit(user)

        # Rule for seperating started and not-startedd decks:
        # A deck is "started" only if the user has at least one persisted Review event for any card inside that deck.
        started_deck_ids = set(
            Review.objects.filter(user=user)
            .values_list('card__deck_id', flat=True)
            .distinct()
        )

        for deck in decks:
            user_cards = CardToUser.objects.filter(card_id__deck=deck, user_id=user.id)
            reviewed_count = user_cards.exclude(review_card={}).count()

            # Show queue-eligible new cards (daily budget aware), not total new cards in deck.
            introduced_today_count = user_cards.filter(new_introduced_on=today).count()
            remaining_budget = max(daily_new_limit - introduced_today_count, 0)
            previously_introduced_new_count = user_cards.filter(review_card={}).exclude(
                new_introduced_on__isnull=True
            ).count()
            not_yet_introduced_new_count = user_cards.filter(
                review_card={},
                new_introduced_on__isnull=True,
            ).count()
            # Some decks may still have unseen cards without CardToUser rows.
            # Include them so a brand-new user sees the expected default "20 new" preview.
            unseen_new_count = max(deck.cards.count() - user_cards.count(), 0)
            introducible_new_count = not_yet_introduced_new_count + unseen_new_count
            deck.cards_new = previously_introduced_new_count + min(
                remaining_budget,
                introducible_new_count,
            )

            # "Learning" means the card has at least one saved review state.
            deck.cards_learning = reviewed_count

            # Preserve original deck order while routing each deck into one section.
            if deck.id in started_deck_ids:
                started_decks.append(deck)
            else:
                not_started_decks.append(deck)
    else:
        for deck in decks:
            deck.cards_new = 0
            deck.cards_learning = 0

    return {
        'decks': decks,
        'started_decks': started_decks,
        'not_started_decks': not_started_decks,
        'available_languages': ["English"],
        'available_languages_to_learn': ["Sora", "Future Language 1", "Future Language 2"],
    }

def all_decks(request):
    context = _get_deck_page_context(request.user)
    context['coming_soon_language'] = request.session.get('coming_soon_language')
    return render(request, 'all_decks.html', context)


@login_required
@require_POST
def set_study_language(request):
    selected_language = (request.POST.get('language') or '').strip()

    if selected_language not in STUDY_LANGUAGES:
        selected_language = "Sora"

    request.session['selected_language_to_learn'] = selected_language

    if selected_language in FUTURE_STUDY_LANGUAGES:
        request.session['coming_soon_language'] = selected_language
    else:
        request.session.pop('coming_soon_language', None)

    return redirect('all_decks:all_decks')


@login_required
def deck_category(request, category):
    context = _get_deck_page_context(request.user)
    # Keep category keys stable for URLs/logic ('started', 'not-started'),
    # user-facing labels use the names ('My Decks', 'Explore Decks').

    if category == 'started':
        context.update(
            {
                'page_title': 'My Decks',
                'category_decks': context['started_decks'],
                'empty_message': "You haven't started any decks yet.",
                'category_description': "Browse every deck that you've started.",
            }
        )
    elif category == 'not-started':
        context.update(
            {
                'page_title': 'Explore Decks',
                'category_decks': context['not_started_decks'],
                'empty_message': "You've started all available decks.",
                'category_description': "Browse every deck that you still have to start.",
            }
        )
    else:
        raise Http404('Deck category not found.')

    return render(request, 'deck_category.html', context)

def about(request):
    return render(request, "about.html")

def contact(request):
    return render(request, "contact.html")

@login_required
def profile(request):
    # Keep settings persisted per user; create defaults automatically on first visit.
    study_settings, _ = UserStudySettings.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserDailyLimitForm(request.POST, instance=study_settings)
        if form.is_valid():
            form.save()
            return redirect('all_decks:profile')
    else:
        form = UserDailyLimitForm(instance=study_settings)

    return render(
        request,
        "profile.html",
        {
            "daily_limit_form": form,
        },
    )

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