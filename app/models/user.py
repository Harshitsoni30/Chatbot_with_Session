from db.session import db
from passlib.context import CryptContext
from bson import ObjectId
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from utils.jwt import decode_access_token
from db.session import db
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
collection = db.users

def register_password(password:str):
    return pwd_context.hash(password)

async def create_user(user):
    user['password'] = register_password(user['password'])
    result = await collection.insert_one(user)
    return str(result.inserted_id)

async def get_user_by_email(email: str):
    return await db.users.find_one({"email": email})

async def get_user_by_username(username: str):
    return await db.users.find_one({"username": username})

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

async def update_user_password(email: str, new_password: str):
    hashed_password = register_password(new_password)
    result = await collection.update_one(
        {"email": email},
        {"$set": {"password": hashed_password}}
    )
    return result.modified_count


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
async def get_current_user(token: str=Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401 , detail="Invalid or expired token")
    
    user = await collection.find_one({'email':payload.get("email")})

    if not user:
        raise HTTPException(status_code=401 , detail="user not found")
    user["token"] = token
    return user

def generate_title(prompt: str) -> str:
    title = prompt.strip().split('.')[0]  # till first period
    if len(title.split()) > 8:
        title = ' '.join(title.split()[:8])
    return title.capitalize()