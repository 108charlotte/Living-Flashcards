from django.core.management.base import BaseCommand
from django.db import ProgrammingError
import requests
from flashcards.models import Deck, CardInfo, CardToUser
import csv
import os
from django.conf import settings
import sys

# claude code to make progress bar
def progress_bar(current, total, width=40):
    filled = int(width * current / total)
    bar = '█' * filled + '░' * (width - filled)
    sys.stdout.write(f'\r|{bar}|')
    sys.stdout.flush()
    if current == total:
        sys.stdout.write('\n')
        sys.stdout.flush()

# used claude for the basic command structure for a django terminal command to update a postgresql database
class Command(BaseCommand): 
    def add_arguments(self, parser): 
        parser.add_argument('--api-path', dest='api_path', type=str)

    def handle(self, *args, **options): 
        api_path = options.get('api_path')

        # clear existing decks and cards (skip if tables don't exist yet)
        try:
            CardToUser.objects.all().delete()
            CardInfo.objects.all().delete()
            Deck.objects.all().delete()

        except ProgrammingError:
            pass  # tables don't exist yet

        api_data = requests.get(api_path)
        api_data = api_data.json() # now python dict

        all_domains = []

        card_infos = []

        sys.stdout.write("\nReading API items\n")

        for i, item in enumerate(api_data, 1): 
            progress_bar(i, len(api_data))
            this_card_domains = []
            try: 
                senses = item.get("senses", [])
                domains = senses[0].get("semantic_domains", []) if senses else []
                for d in domains: 
                    this_card_domains.append(d)
                    if d not in all_domains: 
                        all_domains.append(d)
            except (AttributeError, TypeError, KeyError): 
                domains = None
            
            # claude for error handling
            lexeme = lexeme = item.get("main", {}).get("lexeme", {}).get("default")
            try: 
                en_gloss = item.get("senses", [])[0].get("glosses", {}).get("en")
            except (AttributeError, TypeError, KeyError, IndexError): 
                en_gloss = None
            
            try: 
                audio_path = item.get("audios", [])[0].get("storage_path")
            except (AttributeError, TypeError, KeyError, IndexError): 
                audio_path = None

            # copilot code: require at least a term and an English gloss; include audio when present
            if lexeme and en_gloss:
                card = {
                    "term": lexeme,
                    "definition": en_gloss,
                    "domains": this_card_domains,
                }

                if audio_path:
                    card["audio_path"] = audio_path
                card_infos.append(card)
        
        sys.stdout.write("\nReading semantic domains\n")
        file_path = os.path.join(settings.BASE_DIR, 'flashcards', 'management', 'commands', 'semanticdomains.csv')
        domain_dict = {}
        with open(file_path, 'r', encoding='utf-8') as file: 
            rows = list(csv.DictReader(file))
            for i, row in enumerate(rows, 1): 
                progress_bar(i, len(rows))
                domain_dict[row['Key']] = row['Semantic Domain']

        sys.stdout.write("\nCreating decks\n")
        for i, domain in enumerate(all_domains, 1): 
            progress_bar(i, len(all_domains))
            deck_name = domain_dict.get(domain)
            if deck_name: 
                Deck.objects.get_or_create(name=deck_name)
        
        sys.stdout.write("\nCreating card models\n")
        # claude code caching decks in memory to speed up card creation
        deck_cache = {d.name: d for d in Deck.objects.all()}

        new_cards = []
        for i, card in enumerate(card_infos, 1): 
            progress_bar(i, len(card_infos))
            if not card["domains"]: 
                continue
            deck_name = domain_dict.get(card["domains"][0])
            if not deck_name: 
                continue

            deck = deck_cache.get(deck_name)
            if not deck: 
                continue

            new_cards.append(CardInfo(
                deck=deck,
                term=card["term"],
                definition=card["definition"],
                audio_path=card.get("audio_path")
            ))
        
        CardInfo.objects.bulk_create(new_cards)