"""
Core models for SCG Presales system.
"""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import EmailValidator


class UserManager(BaseUserManager):
    """
    Custom user manager for email-based authentication.
    """
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with an email and password."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with an email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom user model for SCG team members that uses email as username.
    
    This is for team members who access the admin/system, NOT for prospects.
    """
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        help_text="Email address used as username"
    )
    
    # Remove username field
    username = None
    
    # Use email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    # Team role
    role = models.CharField(
        max_length=50,
        choices=[
            ('ADMIN', 'Admin'),
            ('TEAM_SCG', 'Team SCG'),
            ('READ_ONLY', 'Read Only'),
        ],
        default='TEAM_SCG',
        help_text="User role in the system"
    )
    
    # Use the custom manager
    objects = UserManager()
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"