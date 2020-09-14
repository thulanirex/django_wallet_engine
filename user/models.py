from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .managers import WalletUserManager
from phonenumber_field.modelfields import PhoneNumberField

USER_TYPES = [('SUPER_USER','SUPER_USER'),('ADMIN', 'ADMIN'), ('USER','USER')]


class WalletUser(AbstractBaseUser, PermissionsMixin):
    mobileno = PhoneNumberField(_('mobileno'), unique=True)
    name = models.CharField(max_length=50)
    email_id = models.EmailField(max_length=50)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(default=timezone.now)
    user_type = models.CharField(max_length=30,choices=USER_TYPES, default='USER')


    class Meta:
        db_table = "user"
    USERNAME_FIELD = 'mobileno'
    REQUIRED_FIELDS = []

    objects = WalletUserManager()

    def __str__(self):
        return str(self.mobileno) + '_'+ str(self.email_id)+"_"+ str(self.user_type)