from django.urls import path
from . import views

app_name = "lang_selection"

urlpatterns = [
    path('', views.langselection, name='langselection'), 
    path('setlanguage/', views.setlanguage, name='setlanguage'),
]