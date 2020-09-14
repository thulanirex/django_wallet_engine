
import hashlib
SEP_KEY = 'SHA256'
def get_user_hash(*user_data):
    value = ''
    for data in user_data:
        value= value+SEP_KEY+str(data)
    user_hash = hashlib.sha256(str.encode(value)) .hexdigest()
    return user_hash
