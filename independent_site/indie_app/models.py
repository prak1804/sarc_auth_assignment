from django.db import models


class UserProfile(models.Model):
    """
    Local user profile for the Independent Website.

    IMPORTANT: No password field. Passwords live ONLY in the Centralized Auth Service.
    This model stores website-specific data and caches identity info from the auth service.
    """
    # Identity info cached from Centralized Auth Service (read-only reference)
    central_user_id = models.IntegerField(unique=True, help_text="User ID in the Centralized Auth DB")
    username = models.CharField(max_length=150, unique=True)
    name = models.CharField(max_length=255)
    roll_number = models.CharField(max_length=20, unique=True)

    # Independent website-specific fields
    bio = models.TextField(blank=True, default='')
    department = models.CharField(max_length=100, blank=True, default='')
    year_of_study = models.IntegerField(null=True, blank=True)
    profile_picture_url = models.URLField(blank=True, default='')
    joined_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)

    # Django's auth system needs these for admin, etc.
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Required by DRF for authentication
    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'username'

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True

    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.name} ({self.roll_number})"


