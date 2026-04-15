from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserStudySettings

class RegisterForm(UserCreationForm): 
    class Meta: 
        model = User
        fields = ["username", "password1", "password2"]


class UserDailyLimitForm(forms.ModelForm):
    class Meta:
        model = UserStudySettings
        fields = ["daily_new_limit"]
        labels = {
            "daily_new_limit": "Daily per-deck new cards limit, up to:",
        }
        help_texts = {
            "daily_new_limit": "Choose a value from 5 to 30.",
        }