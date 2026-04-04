from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class CentralUserManager(BaseUserManager):
    def create_user(self, username, name, roll_number, hostel_number, password=None):
        if not username:
            raise ValueError('Username is required')
        if not roll_number:
            raise ValueError('Roll number is required')

        user = self.model(
            username=username,
            name=name,
            roll_number=roll_number,
            hostel_number=hostel_number,
        )
        user.set_password(password)  # hashes the password
        user.save(using=self._db)
        return user

    def create_superuser(self, username, name, roll_number, hostel_number, password=None):
        user = self.create_user(username, name, roll_number, hostel_number, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CentralUser(AbstractBaseUser, PermissionsMixin):
    """
    Central user model. This is the ONLY place passwords are stored.
    """
    username = models.CharField(max_length=150, unique=True)
    name = models.CharField(max_length=255)
    roll_number = models.CharField(max_length=20, unique=True)
    hostel_number = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # password field is inherited from AbstractBaseUser (stored as hash)

    objects = CentralUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name', 'roll_number', 'hostel_number']

    class Meta:
        db_table = 'central_users'
        verbose_name = 'Central User'
        verbose_name_plural = 'Central Users'

    def __str__(self):
        return f"{self.username} ({self.roll_number})"
