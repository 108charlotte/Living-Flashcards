from django.urls import path
from . import views

app_name = 'all_decks'
urlpatterns = [
    path('', views.all_decks, name='all_decks'),
    path('study-language/set/', views.set_study_language, name='set_study_language'),
    path('category/<str:category>/', views.deck_category, name='deck_category'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('profile/', views.profile, name='profile'),
    # Copilot generated: Heatmap API endpoint (returns JSON used by the front-end heatmap renderer)
    path('heatmap/data/', views.get_heatmap_data, name='heatmap_data'),
]