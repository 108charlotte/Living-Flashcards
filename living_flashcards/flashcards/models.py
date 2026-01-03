from django.db import models
import uuid
from django.conf import settings
from fsrs import Card
import json

# Create your models here.
class Deck(models.Model): 
    name = models.CharField(max_length=50)
    name_in_lang = models.CharField(max_length=50)

    def __str__(self): 
        return self.name


# used copilot help to define cards in relation to a deck
class CardInfo(models.Model): 
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='cards')
    # for unique identifiers for each card
    card_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    term = models.CharField(max_length=100)
    definition = models.TextField()
    
    def __str__(self): 
        return self.term

class CardToUser(models.Model): 
    # will fix this cascade later if it causes any bugs
    card_id = models.ForeignKey(CardInfo, on_delete=models.CASCADE, related_name="user_cards")
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_cards")
    review_card = models.JSONField(default=dict, blank=True)
    see_next = models.DateTimeField(null=True, blank=True) # helps filter cards for review

    def update_json(self, card): # card is type Card from fsrs library
        self.review_card = card.to_dict()
        self.see_next = card.due
    
    def get_card(self): 
        if self.review_card:
            return Card.from_dict(self.review_card)
        return Card()