from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db import models

from app.utils.watermark import get_watermarked_image


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username and email:
            raise ValueError(_('The username and email must be set'))
        for k, v in extra_fields.items():
            print(f'{k}: {v}')
        email = self.normalize_email(email)
        # if extra_fields.get('image'):
        image = get_watermarked_image(extra_fields['image'])
        user = self.model(username=username, email=email, image=image)
        # else:
        # user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        for k, v in user.__dict__.items():
            print(f'{k}: {v}')
        user.save()

    def create_superuser(self, username, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    genders = [
        ('male', 'male'),
        ('female', 'female'),
        ('other', 'other'),
    ]
    image = models.ImageField(upload_to='user_images/', default='default_user_image.png')
    gender = models.CharField(choices=genders, max_length=6)

    objects = CustomUserManager()

    def __str__(self):
        return self.username
