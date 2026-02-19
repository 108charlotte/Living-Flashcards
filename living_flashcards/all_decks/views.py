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
    if request.user.is_authenticated: 
        # code from copilot to retreive the number of cards to review for each deck before displaying it
        for deck in decks:
            now = timezone.now()
            user_cards = CardToUser.objects.filter(card_id__deck=deck, user_id=request.user.id)
            to_review = (user_cards.filter(see_next__lte=now) | user_cards.filter(see_next__isnull=True))
            deck.cards_to_review = to_review.count()  # set count for template
    else: 
        for deck in decks:
            deck.cards_to_review = 0
    return render(request, 'all_decks.html', {'decks': decks, 'available_languages': ["English"], 'available_languages_to_learn': ["Sora", "Future language 1", "Future language 2"]})

def about(request):
    return render(request, "about.html")

def contact(request):
    return render(request, "contact.html")