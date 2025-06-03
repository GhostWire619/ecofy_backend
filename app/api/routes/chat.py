from fastapi import APIRouter, Depends, HTTPException, status, Body, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import io

from app.api.deps import get_current_user
from app.database import get_db
from app.models.chat import ChatSession, ChatMessage
from app.models.user import User
from app.schemas.chat import ChatSession as ChatSessionSchema
from app.schemas.chat import ChatMessage as ChatMessageSchema
from app.schemas.chat import ChatMessageResponse, MessageType
from app.services.gemini_service import process_text_message, process_audio_message

router = APIRouter()

@router.get("/sessions", response_model=List[ChatSessionSchema])
def get_chat_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(ChatSession).filter(ChatSession.user_id == current_user.id).order_by(ChatSession.created_at.desc()).all()


@router.post("/sessions", response_model=ChatSessionSchema)
def create_chat_session(
    session_data: dict = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    title = session_data.get("title", "New Conversation")
    
    session = ChatSession(
        user_id=current_user.id,
        title=title
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return session


@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
def get_chat_messages(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if session exists and belongs to user
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    return db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at).all()


@router.post("/sessions/{session_id}/messages", response_model=ChatMessageResponse)
async def create_chat_message(
    session_id: str,
    message: ChatMessageSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if session exists and belongs to user
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    # Create user message
    user_message = ChatMessage(
        session_id=session_id,
        user_id=current_user.id,
        content=message.content,
        type=message.type.value,
        file_url=message.file_url,
        is_ai=False
    )
    
    db.add(user_message)
    
    # Update session with last message
    session.last_message = message.content
    session.last_message_time = datetime.utcnow()
    db.add(session)
    
    db.commit()
    db.refresh(user_message)
    
    # Process message with Gemini AI
    ai_content = await process_text_message(message.content, current_user, db)
    
    # Create AI response message
    ai_message = ChatMessage(
        session_id=session_id,
        content=ai_content,
        type=MessageType.TEXT.value,
        is_ai=True
    )
    
    db.add(ai_message)
    db.commit()
    db.refresh(ai_message)
    
    return user_message


@router.post("/sessions/{session_id}/audio", response_model=ChatMessageResponse)
async def create_audio_chat_message(
    session_id: str,
    audio_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if session exists and belongs to user
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    # Read audio file content
    content_type = audio_file.content_type
    audio_bytes = await audio_file.read()
    
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio file uploaded")
    
    # In a real application, you would save the file to storage and generate a URL
    # For simplicity, we'll use a placeholder URL
    file_url = f"/uploads/chat/{session_id}/{audio_file.filename}"
    
    # Create user message for the audio
    user_message = ChatMessage(
        session_id=session_id,
        user_id=current_user.id,
        content="[Audio message]",
        type=MessageType.FILE.value,
        file_url=file_url,
        is_ai=False
    )
    
    db.add(user_message)
    
    # Update session with last message
    session.last_message = "[Audio message]"
    session.last_message_time = datetime.utcnow()
    db.add(session)
    
    db.commit()
    db.refresh(user_message)
    
    try:
        # Process audio with Gemini AI
        ai_audio_bytes = await process_audio_message(audio_bytes, content_type, current_user, db)
        
        # Save AI audio response (in a real app, save to storage)
        ai_file_url = f"/uploads/chat/{session_id}/ai_response_{datetime.utcnow().timestamp()}.mp3"
        
        # Create AI response message
        ai_message = ChatMessage(
            session_id=session_id,
            content="[AI audio response]",
            type=MessageType.FILE.value,
            file_url=ai_file_url,
            is_ai=True
        )
        
        db.add(ai_message)
        db.commit()
    except Exception as e:
        # If audio processing fails, create a text response instead
        ai_message = ChatMessage(
            session_id=session_id,
            content=f"Sorry, I couldn't process your audio. Error: {str(e)}",
            type=MessageType.TEXT.value,
            is_ai=True
        )
        
        db.add(ai_message)
        db.commit()
    
    return user_message 