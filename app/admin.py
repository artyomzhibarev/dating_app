from django.contrib import admin
from .models import User, Match


@admin.register(User)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username', 'email', 'date_joined', 'longitude', 'latitude')
    list_filter = ('date_joined',)


@admin.register(Match)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'liked_user', 'created_at')
