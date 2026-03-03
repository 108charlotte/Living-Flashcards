from django.db import models
import uuid
from django.conf import settings
from fsrs import Card
import json
from django.utils.text import slugify

# Create your models here.
class Deck(models.Model): 
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100)

    def __str__(self): 
        return self.name
    
    # claude code to auto-generate slugs
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

# used copilot help to define cards in relation to a deck
class CardInfo(models.Model): 
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='cards')
    # for unique identifiers for each card
    card_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    term = models.CharField(max_length=100)
    definition = models.TextField()
    audio_path = models.CharField(max_length=400, null=True, blank=True)
    
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
        return Card() # if first call aka no card exists yet

# Copilot generated: Review model to store per-review events for heatmap and analytics
class Review(models.Model):
    """Record of a single review event for heatmap and analytics.

    Stored separately from the CardToUser FSRS state so we have an immutable
    history of when reviews occurred.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    card = models.ForeignKey(CardInfo, on_delete=models.CASCADE, related_name='reviews')
    rating = models.CharField(max_length=16, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review {self.card} by {self.user} at {self.created_at}"