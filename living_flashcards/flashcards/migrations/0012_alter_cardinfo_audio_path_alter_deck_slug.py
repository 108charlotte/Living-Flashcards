from django.db import migrations, models
from django.utils.text import slugify


def populate_missing_deck_slugs(apps, schema_editor):
    Deck = apps.get_model("flashcards", "Deck")

    # Ensure existing rows have non-empty unique slugs before making slug non-null.
    for deck in Deck.objects.filter(slug__isnull=True) | Deck.objects.filter(slug=""):
        base_slug = slugify(deck.name) or f"deck-{deck.pk}"
        candidate_slug = base_slug
        suffix = 1

        while Deck.objects.exclude(pk=deck.pk).filter(slug=candidate_slug).exists():
            candidate_slug = f"{base_slug}-{suffix}"
            suffix += 1

        deck.slug = candidate_slug
        deck.save(update_fields=["slug"])


class Migration(migrations.Migration):

    dependencies = [
        ("flashcards", "0011_delete_decktouser"),
    ]

    operations = [
        migrations.RunPython(populate_missing_deck_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="cardinfo",
            name="audio_path",
            field=models.CharField(blank=True, max_length=400, null=True),
        ),
        migrations.AlterField(
            model_name="deck",
            name="slug",
            field=models.CharField(max_length=100),
        ),
    ]
