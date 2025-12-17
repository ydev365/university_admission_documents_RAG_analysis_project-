from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional


# User Schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Chat Schemas
class ChatRequest(BaseModel):
    subject: str
    question: str


class ChatResponse(BaseModel):
    id: int
    subject: str
    question: str
    answer: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatHistoryResponse(BaseModel):
    histories: List[ChatResponse]
    total: int


class SubjectListResponse(BaseModel):
    subjects: List[str]
