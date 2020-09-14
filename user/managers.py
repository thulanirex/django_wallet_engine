from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _
from django.apps import apps

class WalletUserManager(BaseUserManager):
    """
    Custom user model manager where mobileno is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, mobileno, password,**extra_fields):
        """
        Create and save a User with the given mobileno and password.
        """
        if not mobileno:
            raise ValueError(_('The mobileno must be set'))
        user = self.model(mobileno=mobileno,**extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, mobileno, password, **extra_fields):
        """
        Create and save a SuperUser with the given mobileno and password.
        """

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('user_type', 2)
        return self.create_user(mobileno, password, **extra_fields)
