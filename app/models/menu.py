from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base


class Menu(Base):
    __tablename__ = "menus"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(255), nullable=True)
    parent_id = Column(Integer, ForeignKey("menus.id", ondelete="SET NULL"), nullable=True)
    content = Column(Text, nullable=False)  # Menu content text
    options = Column(JSON, nullable=True)   # JSON field to store menu options
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Self-referential relationship for sub-menus
    parent = relationship("Menu", remote_side=[id], backref="submenus")


class MenuState(Base):
    __tablename__ = "menu_states"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    current_menu = Column(String(100), nullable=True)  # Current menu location
    awaiting_response = Column(Boolean, default=False)  # Flag for if waiting for user response
    form_filled = Column(Boolean, default=False)  # Flag for if form is completed
    context_data = Column(JSON, nullable=True)  # Store any context relevant to current interaction
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship with user
    user = relationship("User", back_populates="menu_state")