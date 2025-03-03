from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime


class MenuBase(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    content: str
    options: Optional[Dict[str, Any]] = None
    is_active: bool = True


class MenuCreate(MenuBase):
    pass


class MenuUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    content: Optional[str] = None
    options: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class MenuInDB(MenuBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class Menu(MenuInDB):
    pass


class MenuWithSubmenus(Menu):
    submenus: List['MenuWithSubmenus'] = []

    class Config:
        orm_mode = True


# Resolve the forward reference
MenuWithSubmenus.update_forward_refs()


class MenuStateBase(BaseModel):
    user_id: int
    current_menu: Optional[str] = None
    awaiting_response: bool = False
    form_filled: bool = False
    context_data: Optional[Dict[str, Any]] = None


class MenuStateCreate(MenuStateBase):
    pass


class MenuStateUpdate(BaseModel):
    current_menu: Optional[str] = None
    awaiting_response: Optional[bool] = None
    form_filled: Optional[bool] = None
    context_data: Optional[Dict[str, Any]] = None


class MenuState(MenuStateBase):
    id: int
    updated_at: datetime

    class Config:
        orm_mode = True


# Schema for WhatsApp interactions
class WhatsAppButtonReply(BaseModel):
    id: str
    title: str


class WhatsAppInteractiveButton(BaseModel):
    type: str = "reply"
    reply: WhatsAppButtonReply


class WhatsAppInteractive(BaseModel):
    type: str = "button"
    body: Dict[str, str]
    action: Dict[str, List[WhatsAppInteractiveButton]]


class WhatsAppMessage(BaseModel):
    messaging_product: str = "whatsapp"
    recipient_type: str = "individual"
    to: str
    type: str
    text: Optional[Dict[str, str]] = None
    interactive: Optional[WhatsAppInteractive] = None


class WhatsAppWebhookMessage(BaseModel):
    from_: str = Field(..., alias="from")
    id: str
    timestamp: str
    type: str
    text: Optional[Dict[str, str]] = None
    interactive: Optional[Dict[str, Any]] = None

    class Config:
        allow_population_by_field_name = True