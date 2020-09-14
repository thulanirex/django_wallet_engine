from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import WalletUser


class WalletUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = WalletUser
        db_table = "user"
        fields = ('mobileno',)

class WalletUserChangeForm(UserChangeForm):

    class Meta:
        model = WalletUser
        fields = ('mobileno',)
        db_table = "user"