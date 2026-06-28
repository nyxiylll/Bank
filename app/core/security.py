import pwdlib


pwd_context = pwdlib.PasswordHash.recommended()


def create_hash(password):
    return pwd_context.hash(password)

def verify_hash(origional_password,hash_password):
    return pwd_context.verify(origional_password,hash_password)
