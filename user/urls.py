from django.urls import path
from .custom_auth_token import CustomObtainAuthToken

urlpatterns = [
path('getToken', CustomObtainAuthToken.as_view(), name='get-token')

]