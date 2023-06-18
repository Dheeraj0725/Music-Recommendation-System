import jwt
import datetime
from datetime import timedelta, datetime
import os
from constant import SECRETKEYS

def generate_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.environ.get(SECRETKEYS.JWT, ''), algorithm=os.environ.get(SECRETKEYS.ALGORITHM))
    return encoded_jwt
