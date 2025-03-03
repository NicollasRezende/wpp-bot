from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=True)
    phone_number = Column(String(50), unique=True, index=True, nullable=False)
    contract_number = Column(String(50), nullable=True)
    terms_accepted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship with the menu state
    menu_state = relationship("MenuState", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    # Relationship with the conversation logs
    conversation_logs = relationship("ConversationLog", back_populates="user", cascade="all, delete-orphan")


class ConversationLog(Base):
    __tablename__ = "conversation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    message = Column(Text, nullable=False)
    direction = Column(String(10), nullable=False)  # 'incoming' or 'outgoing'
    menu_option = Column(String(50), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship with user
    user = relationship("User", back_populates="conversation_logs")