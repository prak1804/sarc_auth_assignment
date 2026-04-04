from rest_framework import serializers
from .models import CentralUser


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = CentralUser
        fields = ['username', 'name', 'roll_number', 'hostel_number', 'password']

    def validate_roll_number(self, value):
        if CentralUser.objects.filter(roll_number=value).exists():
            raise serializers.ValidationError("A user with this roll number already exists.")
        return value

    def create(self, validated_data):
        user = CentralUser.objects.create_user(
            username=validated_data['username'],
            name=validated_data['name'],
            roll_number=validated_data['roll_number'],
            hostel_number=validated_data['hostel_number'],
            password=validated_data['password'],
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CentralUser
        fields = ['id', 'username', 'name', 'roll_number', 'hostel_number', 'created_at']
        read_only_fields = fields
