from django.core.management.base import BaseCommand
from flashcards.models import CardInfo
class Command(BaseCommand): 
    def handle(self, *args, **options):
        for card in CardInfo.objects.all():
            print(card.id, card.term, card.audio_path)
            # looks like this: sora/audio/local_import/2011-9-15-Sora-6-30-MR-leech-bst-1580869882041.mp3
            # want it to be everything after local_import
            if card.audio_path: 
                card.audio_path = card.audio_path[24:]
                card.save()