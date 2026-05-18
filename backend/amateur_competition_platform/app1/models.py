from django.db import models

# Create your models here.
#python manage.py makemigrations
#python manage.py migrate
class User(models.Model):
    username = models.CharField(max_length=32)
    password = models.CharField(max_length=64)

