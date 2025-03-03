from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    phone_number: str = Field(..., min_length=8, max_length=20)
    name: Optional[str] = None
    contract_number: Optional[str] = None
    terms_accepted: bool = False


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: Optional[str] = None
    contract_number: Optional[str] = None
    terms_accepted: Optional[bool] = None


class UserInDB(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class User(UserInDB):
    pass


class ConversationLogBase(BaseModel):
    message: str
    direction: str
    menu_option: Optional[str] = None


class ConversationLogCreate(ConversationLogBase):
    user_id: int


class ConversationLog(ConversationLogBase):
    id: int
    user_id: int
    timestamp: datetime

    class Config:
        orm_mode = True


class UserWithLogs(User):
    conversation_logs: List[ConversationLog] = []

    class Config:
        orm_mode = True