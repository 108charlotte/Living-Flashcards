from django.urls import path
from . import views

app_name = "authentication"

urlpatterns = [
    path('sign-up/', views.sign_up, name='sign-up'),
]