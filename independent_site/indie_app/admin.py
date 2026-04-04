from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['username', 'name', 'roll_number', 'department', 'year_of_study', 'joined_at']
    search_fields = ['username', 'name', 'roll_number']
    readonly_fields = ['central_user_id', 'username', 'name', 'roll_number', 'joined_at', 'last_seen']
