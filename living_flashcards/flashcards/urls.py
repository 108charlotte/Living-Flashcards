from django.urls import path
from . import views

app_name = "flashcards"

urlpatterns = [
    path('review/', views.review_card, name='review_card'), 
    path('<str:slug>/', views.flashcards, name='flashcards'),
]