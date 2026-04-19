from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class UserStudySettings(models.Model):
	user = models.OneToOneField(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='study_settings',
	)
	# User-configurable cap for how many brand-new cards can appear in one queue build.
	daily_new_limit = models.PositiveSmallIntegerField(
		default=20,
		validators=[MinValueValidator(5), MaxValueValidator(30)],
	)
	# here since this is the only place to store user-specific custom information
	# this is a date storing when the user opened their first deck. this will allow us to show update notes to users in the future if we change parts of the flashcard experience, rather than only showing the about screen as a one-off
	first_deck_opened = models.DateTimeField(null=True, blank=True)

	def __str__(self):
		return f"Study settings for {self.user}"