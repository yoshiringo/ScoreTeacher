from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Account(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    last_name = models.CharField(max_length=100, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    account_image = models.ImageField(upload_to="profile_pics",blank=True)

    def __str__(self):
        return self.user.username