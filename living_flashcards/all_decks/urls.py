from django.urls import path
from . import views

app_name = 'all_decks'

urlpatterns = [
    path('', views.all_decks, name='all_decks'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
]