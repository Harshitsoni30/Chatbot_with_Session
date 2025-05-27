from datetime import datetime, timedelta
from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta
from jose import JWTError, jwt
from dotenv import load_dotenv
import os
from typing import Set
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
algorithm = os.getenv("ALGORITHM")

ACCESS_TOKEN_EXPIRE_DAYS = 1  


def create_access_token(data: dict):
    to_encode = data.copy()
    
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)

    print(expire)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=algorithm)

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[algorithm])
        return payload
    except ExpiredSignatureError:
        print("Token expired.")
        return None
    except JWTError:
        print("Invalid token.")
        return None


