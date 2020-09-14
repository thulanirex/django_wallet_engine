import hashlib
from django.conf import settings


def get_user_hash(user_data,currency='SGD'):
    value= settings.HASH_KEY+ str(user_data)+currency+settings.HASH_KEY
    user_hash = hashlib.sha256(str.encode(value)) .hexdigest()
    return user_hash
