from django.db import models
from django.conf import settings

# Create your models here.
class UserLanguage(models.Model): 
    djangousermodel = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    language = models.CharField(max_length=20, default='en')