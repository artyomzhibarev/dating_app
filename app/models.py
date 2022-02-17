from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db.models.expressions import RawSQL
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.conf import settings
import math
from django.db.backends.signals import connection_created
from django.dispatch import receiver

from app.utils.watermark import get_watermarked_image


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username and email:
            raise ValueError(_('The username and email must be set'))
        email = self.normalize_email(email)
        data = {'username': username, 'email': email}
        if extra_fields.get('image'):
            image = get_watermarked_image(extra_fields['image'])
            data.update({'image': image})
        user = self.model(**data)
        user.set_password(password)
        # for k, v in user.__dict__.items():
        #     print(f'{k}: {v}')
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
    longitude = models.DecimalField(max_digits=9, decimal_places=6, default=0.0)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, default=0.0)

    objects = CustomUserManager()

    def __str__(self):
        return self.username


class Match(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  on_delete=models.CASCADE,
                                  related_name='user_matches')  # who liked
    liked_user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.CASCADE)  # who was liked
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'From: {self.from_user}, To: {self.liked_user}'


# @receiver(connection_created)
# def extend_sqlite(connection=None, **kwargs):
#     cf = connection.connection.create_function
#     cf('acos', 1, math.acos)
#     cf('cos', 1, math.cos)
#     cf('radians', 1, math.radians)
#     cf('sin', 1, math.sin)
#     cf('least', 2, min)
#     cf('greatest', 2, max)


def get_locations_nearby_coords(latitude, longitude, max_distance=None):
    """
    Return objects sorted by distance to specified coordinates
    which distance is less than max_distance given in kilometers
    """
    # Great circle distance formula
    gcd_formula = "6371 * acos(least(greatest(\
    cos(radians(%s)) * cos(radians(latitude)) \
    * cos(radians(longitude) - radians(%s)) + \
    sin(radians(%s)) * sin(radians(latitude)) \
    , -1), 1))"
    distance_raw_sql = RawSQL(
        gcd_formula,
        (latitude, longitude, latitude)
    )
    qs = User.objects.all().annotate(distance=distance_raw_sql).order_by('distance')
    if max_distance is not None:
        qs = qs.filter(distance__lt=max_distance)
    return qs
