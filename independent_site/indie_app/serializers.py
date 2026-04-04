from rest_framework import serializers
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'id', 'username', 'name', 'roll_number',
        ]
        read_only_fields = ['id', 'username', 'name', 'roll_number']


class RegisterForwardSerializer(serializers.Serializer):
    """
    Used when registration happens on the independent website.
    Collects all required fields to forward to the Centralized Auth Service.
    """
    username = serializers.CharField(max_length=150)
    name = serializers.CharField(max_length=255)
    roll_number = serializers.CharField(max_length=20)
    hostel_number = serializers.CharField(max_length=10)
    password = serializers.CharField(write_only=True, min_length=8)
    # Independent-site-specific optional fields
    department = serializers.CharField(max_length=100, required=False, allow_blank=True)
    year_of_study = serializers.IntegerField(required=False, allow_null=True)
