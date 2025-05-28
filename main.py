from typing import Annotated
from fastapi import FastAPI, HTTPException, status, Depends
from app.schemas.auth import UserRegister, UserOut, UserLogin, TokenVerify, ResetPassword, OTPVerifyRequest, ForgotPasswordRequest, VerifyOTPRequest, SessionCreate
from app.schemas.auth import ChatSessionInput, ChatHistroyInput ,PDFUpload
from app.models.user import create_user, get_user_by_email, get_user_by_username,verify_password, update_user_password, get_current_user, generate_title
from bson import ObjectId
from fastapi import FastAPI, Form
from app.validations.sender_email import generate_otp, send_otp_email
from fastapi import HTTPException, status
from app.utils.jwt import create_access_token
from datetime import timedelta
from jose import JWTError, jwt
from dotenv import load_dotenv
import os
from typing import Set
from uuid import uuid4
from datetime import datetime
from app.db.session import session_collection, session_title_collection
from fastapi import FastAPI, Request
from pydantic import BaseModel
from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.duckduckgo import DuckDuckGo
from dotenv import load_dotenv
import os
from fastapi import Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import asyncio
import json
from fastapi import UploadFile, File, Form
import shutil
import os
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from datetime import datetime
from app.routers.agent import create_agent, load_combined_knowledge_base
import os
from fastapi import FastAPI, File, UploadFile, Form


load_dotenv()
blacklisted_tokens: Set[str] = set()
SECRET_KEY = os.getenv("SECRET_KEY")
algorithm = os.getenv("ALGORITHM")

app = FastAPI()

origins = [
    '*'
    # Add other origins as needed
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows specified origins
    allow_credentials=True,
    allow_methods=["*"],    # Allows all HTTP methods
    allow_headers=["*"],    # Allows all headers
)




otp_storage = {}
@app.post("/register", response_model=UserOut)
async def register_user(user : UserRegister):
    existing_user = await get_user_by_email(user.email)
    existing_user_username = await get_user_by_username(user.username)
    if existing_user or existing_user_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user already exists"
        )

    user_dict = user.dict()
    user_id = await create_user(user_dict)

    return {
        "id": user_id,
        "username":user.username,
        "email": user.email
    }
@app.post("/register-send-otp")
async def send_otp(user : UserRegister):
    existing_user = await get_user_by_email(user.email)
    existing_user_username = await get_user_by_username(user.username)
    if existing_user or existing_user_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user already exists"
        )
    otp= generate_otp()
    otp_storage[user.email]={
        "otp":otp,
        "user_data":user.dict()
    }
    await send_otp_email(user.email, otp)
    return {"message": "OTP sent to your email"}


@app.post("/register-verify-otp")
async def verify_otp(data: OTPVerifyRequest):
    email = data.email
    otp = data.otp

    if email not in otp_storage:
        raise HTTPException(status_code=404, detail="OTP not requested")

    stored = otp_storage[email]
    if stored["otp"] != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # OTP is correct — create user
    user_data = stored["user_data"]
    user_id = await create_user(user_data)

    del otp_storage[email]

    return {"message": "User registered successfully", "user_id": user_id}

@app.post("/login")
async def request_login_user(user:UserLogin):
    db_user =await get_user_by_email(user.email)
    if not db_user:
        raise HTTPException(status_code=404,detail="User not found")
    if not verify_password(user.password, db_user['password']):
        raise HTTPException(status_code=401,detail="Incorrect password")
    
    token = create_access_token(
        data={"email":user.email},
        
    )
    return {
        "token":token,
        "email": db_user["email"],
        "username": db_user["username"]
    }

@app.post("/logout")
async def logout_user(data: TokenVerify):
    try:
        payload = jwt.decode(data.token, SECRET_KEY, algorithms=[algorithm])
        email = payload.get("email")
        if email != data.email:
            raise HTTPException(status_code=401, detail="Invalid email")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    blacklisted_tokens.add(data.token)
    return {"message": "Logged out successfully"}

@app.post("/reset-password")
async def reset_password(user : ResetPassword):
        db_user =await get_user_by_email(user.email)
        if not db_user:
            raise HTTPException(status_code=404,detail="User not found")
        if not verify_password(user.password, db_user['password']):
            raise HTTPException(status_code=401,detail="Incorrect password")
        
        await update_user_password(user.email ,user.new_password)

        return {
            "message": "Password updated successfully"
        }
        
@app.post("/forgot-request")
async def forgot_password_request(user: ForgotPasswordRequest):
    db_user =await get_user_by_email(user.email)
    if not db_user:
        raise HTTPException(status_code=404,detail="User not found")
    otp= generate_otp()
    otp_storage[user.email]={
        "otp":otp,
        "user_data":user.dict()
    }
    await send_otp_email(user.email, otp)
    return {"message": "OTP sent to your email"}
    
@app.post("/forgot-response")
async def forgot_password_response(data:VerifyOTPRequest):
    email=data.email
    otp=data.otp
    if email not in otp_storage:
        raise HTTPException(status_code=404, detail="OTP not requested")
    stored = otp_storage[email]
    if stored["otp"] != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    await update_user_password(data.email ,data.new_password)
    del otp_storage[email]
    return {
            "message": "Password updated successfully"
        }


@app.post("/session/create")
async def create_session(current_user: dict = Depends(get_current_user)):
    session_id =str(uuid4())
    session = SessionCreate(
        session_id=session_id,
        user_email=current_user["email"],
        created_at=datetime.utcnow(),   
    )

    await session_collection.insert_one(session.dict())
    return {"message":"Session is created",
            "session_id":session_id}


@app.get("/chat-history")
async def get_chat_history(current_user: dict= Depends(get_current_user)):
    session_cursor = await session_collection.find(
        {
            "user_email": current_user['email']
        }
    ).to_list(length=None)

    if not session_cursor:
        return {"sessions": []}  
    # Convert ObjectId to string and rename to 'id'
    for session in session_cursor:
        session['id'] = str(session['_id'])
        del session['_id']

    return {"sessions": session_cursor}

@app.get("/single-session")
async def get_chat_history_single_user(
    session_id: str = Query(...),  # Take session_id as a query parameter
    current_user: dict = Depends(get_current_user)
):
    query = {
        "user_email": current_user["email"],
        "session_id": session_id
    }

    chats_cursor = session_title_collection.find(query)
    chats = await chats_cursor.to_list(length=1000)

    if not chats:
        raise HTTPException(status_code=404, detail="No chats found for this session")
    for chat in chats:
        chat["id"] = str(chat["_id"])
        del chat["_id"]
    return {"chats": chats}


@app.post("/session/chat")
async def create_chat_session_stream(chat_data: ChatSessionInput):
    session_id = chat_data.session_id
    prompt = chat_data.prompt

    print(prompt)
    pdf_path = os.path.join(UPLOAD_DIR, f"{session_id}.pdf")
    
    knowledge = load_combined_knowledge_base(pdf_path)
    agent = create_agent(knowledge=knowledge)

    existing_session = await session_title_collection.find_one({
        "session_id": session_id
    })

    chat_history_prompt = ""
    if existing_session and "message" in existing_session:
        for msg in existing_session["message"]:
            chat_history_prompt += f"{msg['role'].capitalize()}: {msg['content']}\n"

    full_prompt = chat_history_prompt + f"User: {prompt}\nAssistant:"
    full_response = ""

    async def stream_response():
        nonlocal full_response
        
        response = agent.run(prompt, stream=True)
        # breakpoint()
        # print(response.content)
        for chunk in response:
            if chunk and chunk.content:
                full_response += chunk.content
                yield chunk.content
        print("full_response",full_response)

        # Store messages
        user_msg = {"role": "user", "content": prompt}
        assistant_msg = {"role": "assistant", "content": full_response}

        if existing_session:
            await session_title_collection.update_one(
                {"session_id": session_id},
                {
                    "$push": {"message": {"$each": [user_msg, assistant_msg]}},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
        else:
            title = generate_title(prompt)
            new_session = {
                "session_id": session_id,
                "title": title,
                "message": [user_msg, assistant_msg],
                "created_at": datetime.utcnow()
            }
            await session_title_collection.insert_one(new_session)

    return StreamingResponse(
        stream_response(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        },
    )


UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload/pdf")
async def upload_pdf(
    session_id: str = Form(...),
    uploaded_pdf: UploadFile = File(...)
):
    file_path = os.path.join(UPLOAD_DIR, f"{session_id}.pdf")
    with open(file_path, "wb") as f:
        shutil.copyfileobj(uploaded_pdf.file, f)
    
    return {"message": "File uploaded successfully", "file_path": file_path}
