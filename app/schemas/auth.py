from fastapi import File, UploadFile
from pydantic import BaseModel, EmailStr, Field
from typing import Literal,List
from datetime import datetime


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserOut(BaseModel):
    id: str
    username: str
    email: EmailStr

class UserLogin(BaseModel):
    email:EmailStr
    password:str

class TokenVerify(BaseModel):
    email:str
    token:str

class ResetPassword(BaseModel):
    email:str
    password:str
    new_password:str

class OTPVerifyRequest(BaseModel):
    email: str
    otp: str

class ForgotPasswordRequest(BaseModel):
    email:EmailStr

class VerifyOTPRequest(BaseModel):
    email:EmailStr
    otp:str
    new_password:str

class MessageCreate(BaseModel):
    session_id:str
    content:str
    sender: Literal["user", "assistant"]

class SessionCreate(BaseModel):
    session_id: str
    user_email: EmailStr
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ChatSessionInput(BaseModel):
    session_id: str
    prompt: str
    

class ChatHistroyInput(BaseModel):
    session_id :str

class PDFUpload(BaseModel):
    session_id :str
    uploaded_pdf :UploadFile = File(...)
    
