from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CentralUser


@admin.register(CentralUser)
class CentralUserAdmin(UserAdmin):
    list_display = ['username', 'name', 'roll_number', 'hostel_number', 'is_active', 'created_at']
    search_fields = ['username', 'name', 'roll_number']
    ordering = ['-created_at']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('name', 'roll_number', 'hostel_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'name', 'roll_number', 'hostel_number', 'password1', 'password2'),
        }),
    )
