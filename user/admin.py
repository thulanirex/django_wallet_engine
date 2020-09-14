from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import WalletUserCreationForm, WalletUserChangeForm
from .models import WalletUser


class WalletUserAdmin(UserAdmin):
    add_form = WalletUserCreationForm
    form = WalletUserChangeForm
    model = WalletUser
    exclude = ('is_staff','is_superuser','last_login')
    list_display = ('mobileno', 'name', 'email_id', 'user_type','is_active',)
    list_filter = ('mobileno', 'name', 'email_id' , 'user_type','is_active',)
    fieldsets = ((None, {'fields': ('mobileno', 'password','name', 'email_id', 'user_type',)}),
                 ('Permissions', {'fields': ( 'is_active',)}),)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('mobileno', 'name', 'email_id', 'user_type','password1', 'password2','is_active',)}
        ),
    )
    search_fields = ('mobileno',)
    ordering = ('mobileno',)


admin.site.register(WalletUser, WalletUserAdmin)