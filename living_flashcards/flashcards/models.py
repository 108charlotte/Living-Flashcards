from django.db import models
import uuid

# Create your models here.
class Deck(models.Model): 
    name = models.CharField(max_length=50)
    name_in_lang = models.CharField(max_length=50)

    def __str__(self): 
        return self.name

# used copilot help to define cards in relation to a deck
class Card(models.Model): 
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='cards')
    # for unique identifiers for each card
    card_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    term = models.CharField(max_length=100)
    definition = models.TextField()
    last_seen = models.DateTimeField(null=True, blank=True)
    confidence_score = models.IntegerField(default=0)
    see_next = models.DateTimeField(null=True, blank=True)

    def __str__(self): 
        return self.term