import os
import random
import string
import httpx
import json
from typing import List, Dict, Any, Optional, Union
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from datetime import datetime

from config.settings import settings
from app.db.crud.user import user as user_crud, conversation_log
from app.schemas.menu import WhatsAppMessage


class WhatsAppService:
    def __init__(self):
        self.base_url = settings.BASE_URL
        self.page_id = settings.PAGE_ID
        self.token = settings.WHATSAPP_TOKEN
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    async def send_message(self, phone_number: str, message: str, log_to_db: bool = True, user_id: Optional[int] = None, db: Optional[Session] = None) -> Dict[str, Any]:
        """
        Send a text message to a WhatsApp user
        """
        url = f"{self.base_url}/{self.page_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "text",
            "text": {"body": message}
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=payload)
            
            if response.status_code >= 400:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"WhatsApp API error: {response.text}"
                )
                
            # Log the message to the database if requested
            if log_to_db and db and user_id:
                conversation_log.create_log(
                    db=db,
                    user_id=user_id,
                    message=message,
                    direction="outgoing"
                )
                
            return response.json()

    async def send_template_message(
        self, 
        phone_number: str, 
        template_name: str,
        language_code: str = "pt_BR",
        components: List[Dict[str, Any]] = None,
        log_to_db: bool = True,
        user_id: Optional[int] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Send a template message to a WhatsApp user
        """
        url = f"{self.base_url}/{self.page_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code
                }
            }
        }
        
        if components:
            payload["template"]["components"] = components
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=payload)
            
            if response.status_code >= 400:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"WhatsApp API error: {response.text}"
                )
                
            # Log the message to the database if requested
            if log_to_db and db and user_id:
                message_summary = f"Template message: {template_name}"
                conversation_log.create_log(
                    db=db,
                    user_id=user_id,
                    message=message_summary,
                    direction="outgoing"
                )
                
            return response.json()

    async def send_button_message(
        self,
        phone_number: str,
        body_text: str,
        buttons: List[Dict[str, str]],
        log_to_db: bool = True,
        user_id: Optional[int] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Send an interactive message with buttons to a WhatsApp user
        
        Example buttons format:
        [
            {"id": "button1", "title": "Button 1"},
            {"id": "button2", "title": "Button 2"}
        ]
        """
        url = f"{self.base_url}/{self.page_id}/messages"
        
        # Format buttons according to WhatsApp API requirements
        formatted_buttons = [
            {
                "type": "reply",
                "reply": {
                    "id": button["id"],
                    "title": button["title"]
                }
            } for button in buttons
        ]
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": body_text},
                "action": {
                    "buttons": formatted_buttons
                }
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=payload)
            
            if response.status_code >= 400:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"WhatsApp API error: {response.text}"
                )
                
            # Log the message to the database if requested
            if log_to_db and db and user_id:
                button_titles = [button["title"] for button in buttons]
                message_summary = f"Button message: {body_text} with options: {', '.join(button_titles)}"
                conversation_log.create_log(
                    db=db,
                    user_id=user_id,
                    message=message_summary,
                    direction="outgoing"
                )
                
            return response.json()

    async def send_list_message(
        self,
        phone_number: str,
        header_text: str,
        body_text: str,
        footer_text: str,
        button_text: str,
        sections: List[Dict[str, Any]],
        log_to_db: bool = True,
        user_id: Optional[int] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Send an interactive list message to a WhatsApp user
        
        Example sections format:
        [
            {
                "title": "Section 1",
                "rows": [
                    {"id": "option1", "title": "Option 1", "description": "Description 1"},
                    {"id": "option2", "title": "Option 2", "description": "Description 2"}
                ]
            }
        ]
        """
        url = f"{self.base_url}/{self.page_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {
                    "type": "text",
                    "text": header_text
                },
                "body": {
                    "text": body_text
                },
                "footer": {
                    "text": footer_text
                },
                "action": {
                    "button": button_text,
                    "sections": sections
                }
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=payload)
            
            if response.status_code >= 400:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"WhatsApp API error: {response.text}"
                )
                
            # Log the message to the database if requested
            if log_to_db and db and user_id:
                message_summary = f"List message: {body_text}"
                conversation_log.create_log(
                    db=db,
                    user_id=user_id,
                    message=message_summary,
                    direction="outgoing"
                )
                
            return response.json()
            
    async def send_link_message(
        self,
        phone_number: str,
        title: str,
        body_text: str,
        url: str,
        button_text: str = "Click here",
        log_to_db: bool = True,
        user_id: Optional[int] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Send a message with a clickable link
        """
        api_url = f"{self.base_url}/{self.page_id}/messages"
        
        message_text = f"*{title}*\n\n{body_text}"
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "cta_url",
                "body": {"text": message_text},
                "action": {
                    "name": "cta_url",
                    "parameters": {
                        "display_text": button_text,
                        "url": url
                    }
                }
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, headers=self.headers, json=payload)
            
            if response.status_code >= 400:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"WhatsApp API error: {response.text}"
                )
                
            # Log the message to the database if requested
            if log_to_db and db and user_id:
                message_summary = f"Link message: {title} - {url}"
                conversation_log.create_log(
                    db=db,
                    user_id=user_id,
                    message=message_summary,
                    direction="outgoing"
                )
                
            return response.json()

    async def upload_media(self, file: UploadFile) -> str:
        """
        Upload media to WhatsApp servers and get media ID
        """
        url = f"{self.base_url}/{self.page_id}/media"
        
        headers = {
            "Authorization": f"Bearer {self.token}",
        }
        
        form_data = {
            "messaging_product": "whatsapp",
            "file": file.file
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url, 
                headers=headers, 
                files={"file": (file.filename, await file.read(), file.content_type)},
                data={"messaging_product": "whatsapp"}
            )
            
            if response.status_code >= 400:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"WhatsApp API error: {response.text}"
                )
                
            media_id = response.json().get("id")
            if not media_id:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to get media ID from WhatsApp API"
                )
                
            return media_id

    async def send_media_message(
        self,
        phone_number: str,
        media_id: str,
        media_type: str,  # "image", "document", "audio", "video", "sticker"
        filename: Optional[str] = None,
        caption: Optional[str] = None,
        log_to_db: bool = True,
        user_id: Optional[int] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Send a media message to a WhatsApp user
        """
        url = f"{self.base_url}/{self.page_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": media_type,
            media_type: {
                "id": media_id
            }
        }
        
        if caption and media_type in ["image", "video", "document"]:
            payload[media_type]["caption"] = caption
            
        if filename and media_type == "document":
            payload[media_type]["filename"] = filename
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=payload)
            
            if response.status_code >= 400:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"WhatsApp API error: {response.text}"
                )
                
            # Log the message to the database if requested
            if log_to_db and db and user_id:
                message_summary = f"Media message type: {media_type}"
                if caption:
                    message_summary += f" with caption: {caption}"
                conversation_log.create_log(
                    db=db,
                    user_id=user_id,
                    message=message_summary,
                    direction="outgoing"
                )
                
            return response.json()

    async def send_location_message(
        self,
        phone_number: str,
        latitude: str,
        longitude: str,
        name: str,
        address: str,
        log_to_db: bool = True,
        user_id: Optional[int] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Send a location message to a WhatsApp user
        """
        url = f"{self.base_url}/{self.page_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "location",
            "location": {
                "latitude": latitude,
                "longitude": longitude,
                "name": name,
                "address": address
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=payload)
            
            if response.status_code >= 400:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"WhatsApp API error: {response.text}"
                )
                
            # Log the message to the database if requested
            if log_to_db and db and user_id:
                message_summary = f"Location message: {name} - {address}"
                conversation_log.create_log(
                    db=db,
                    user_id=user_id,
                    message=message_summary,
                    direction="outgoing"
                )
                
            return response.json()

    async def send_contact_message(
        self,
        phone_number: str,
        contact_name: str,
        contact_phone: str,
        log_to_db: bool = True,
        user_id: Optional[int] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Send a contact message to a WhatsApp user
        """
        url = f"{self.base_url}/{self.page_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "contacts",
            "contacts": [{
                "name": {
                    "first_name": contact_name,
                    "formatted_name": contact_name
                },
                "phones": [{
                    "phone": contact_phone,
                    "wa_id": contact_phone,
                    "type": "CELL"
                }]
            }]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=payload)
            
            if response.status_code >= 400:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"WhatsApp API error: {response.text}"
                )
                
            # Log the message to the database if requested
            if log_to_db and db and user_id:
                message_summary = f"Contact message: {contact_name} - {contact_phone}"
                conversation_log.create_log(
                    db=db,
                    user_id=user_id,
                    message=message_summary,
                    direction="outgoing"
                )
                
            return response.json()

    @staticmethod
    def generate_random_code(length: int = 10) -> str:
        """
        Generate a random alphanumeric code
        """
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))


# Create a singleton instance
whatsapp_service = WhatsAppService()