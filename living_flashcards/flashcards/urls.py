from django.urls import path
from . import views

urlpatterns = [
    path('flashcards/', views.flashcards, name='flashcards'),
]