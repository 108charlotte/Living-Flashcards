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

    # for spaced repetition, will have a func to convert this to the nearest character
    # 0.05 = 5 minutes
    # 0.10 = 10 minutes
    # 0.15 = 15 minutes
    # 0.20 = 20 minutes
    # 0.30 = 30 minutes
    # 1 = 1 day
    # 2 = 2 days
    # 3 = 3 days

    # arbitrary value for max_digits, see above for why 2 decimal places, null until 1st review
    easy_interval = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    good_interval = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    hard_interval = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    again_interval = models.DecimalField(max_digits=6, decimal_places=2, null=True)

    def __str__(self): 
        return self.term