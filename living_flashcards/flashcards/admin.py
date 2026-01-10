from django.contrib import admin
from .models import Deck, CardInfo, CardToUser

# Register your models here.
admin.site.register(Deck)
admin.site.register(CardInfo)
admin.site.register(CardToUser)