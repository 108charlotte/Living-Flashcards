from django.urls import path
from . import views

app_name = "flashcards"

urlpatterns = [
    path('review/', views.review_card, name='review_card'),
    path('<str:slug>/practice/', views.flashcards, name='flashcards'),
    path('<str:slug>/', views.deck_preview, name='deck_preview'),
]