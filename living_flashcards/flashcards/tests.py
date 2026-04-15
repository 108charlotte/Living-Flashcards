from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import CardInfo, CardToUser, Deck, Review


class FlashcardsAuthRegressionTests(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(
			username='test-user',
			password='test-password-123',
		)
		self.deck = Deck.objects.create(name='Numbers', slug='numbers')
		self.card = CardInfo.objects.create(
			deck=self.deck,
			term='one',
			definition='1',
		)

	def test_flashcards_redirects_anonymous_users_to_login(self):
		flashcards_url = reverse('flashcards:flashcards', args=[self.deck.slug])
		response = self.client.get(flashcards_url)

		self.assertEqual(response.status_code, 302)
		self.assertEqual(response['Location'], f"{settings.LOGIN_URL}?next={flashcards_url}")

	def test_review_card_redirects_anonymous_users_to_login(self):
		review_url = reverse('flashcards:review_card')
		response = self.client.post(
			review_url,
			{'rating': 'good', 'card_id': str(self.card.card_id)},
		)

		self.assertEqual(response.status_code, 302)
		self.assertEqual(response['Location'], f"{settings.LOGIN_URL}?next={review_url}")

	def test_authenticated_user_can_open_flashcards_and_gets_card_state(self):
		self.client.force_login(self.user)

		response = self.client.get(reverse('flashcards:flashcards', args=[self.deck.slug]))

		self.assertEqual(response.status_code, 200)
		self.assertTrue(
			CardToUser.objects.filter(card_id=self.card, user_id=self.user).exists()
		)

	def test_authenticated_user_can_submit_review_and_review_event_is_recorded(self):
		self.client.force_login(self.user)
		self.client.get(reverse('flashcards:flashcards', args=[self.deck.slug]))

		card_to_user = CardToUser.objects.get(card_id=self.card, user_id=self.user)
		response = self.client.post(
			reverse('flashcards:review_card'),
			{'rating': 'good', 'card_id': str(self.card.card_id)},
		)

		card_to_user.refresh_from_db()

		self.assertEqual(response.status_code, 200)
		self.assertIsNotNone(card_to_user.see_next)
		self.assertTrue(card_to_user.review_card)
		self.assertTrue(
			Review.objects.filter(user=self.user, card=self.card, rating='good').exists()
		)
