from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.conf import settings
from flashcards.models import Deck
from django.utils import timezone
from flashcards.models import CardToUser

# Create your views here.

def all_decks(request):
    decks = Deck.objects.all()
    # code from copilot to retreive the number of cards to review for each deck before displaying it
    for deck in decks:
        now = timezone.now()
        user_cards = CardToUser.objects.filter(card_id__deck=deck, user_id=request.user)
        to_review = (user_cards.filter(see_next__lte=now) | user_cards.filter(see_next__isnull=True))
        deck.cards_to_review = to_review.count()  # Set count for template
    return render(request, 'all_decks.html', {'decks': decks, 'available_languages': ["English"], 'available_languages_to_learn': ["Sora"]})