from fastapi import APIRouter, Depends, HTTPException, Request, Response, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import json
import logging
import os

from config.settings import settings
from config.database import get_db
from app.db.crud.user import user as user_crud, conversation_log
from app.models.user import User
from app.services.whatsapp import whatsapp_service
from app.services.menu import MenuService
from app.utils.helpers import is_greeting, is_business_hours, format_phone_number
from app.utils.constants import MenuType


# Create logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.get("/webhook")
async def verify_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Verification endpoint for WhatsApp webhook
    """
    query_params = dict(request.query_params)
    
    verify_token = query_params.get("hub.verify_token")
    
    if verify_token == settings.VERIFY_TOKEN:
        return Response(content=query_params.get("hub.challenge"), media_type="text/plain")
        
    return Response(content="Verification failed", status_code=403)


@router.post("/webhook")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Receive webhook notifications from WhatsApp
    """
    try:
        data = await request.json()
        
        # Log incoming webhook data
        logger.debug(f"Webhook data: {json.dumps(data, indent=2)}")
        
        if "object" not in data:
            return Response(content="Invalid request", status_code=400)
            
        if data["object"] != "whatsapp_business_account":
            return Response(content="Invalid request", status_code=400)
            
        # Process entries asynchronously to avoid webhook timeout
        background_tasks.add_task(process_webhook_entries, data, db)
            
        return {"status": "processing"}
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return Response(content=f"Error: {str(e)}", status_code=500)


async def process_webhook_entries(data: Dict[str, Any], db: Session):
    """
    Process webhook entries asynchronously
    """
    menu_service = MenuService(
        menu_crud=None,  # To be properly initialized
        menu_state_crud=None,  # To be properly initialized 
        user_crud=user_crud,
        log_crud=conversation_log
    )
    
    try:
        if "entry" not in data:
            logger.error("No entries in webhook data")
            return
            
        for entry in data["entry"]:
            if "changes" not in entry:
                continue
                
            for change in entry["changes"]:
                if "value" not in change:
                    continue
                    
                value = change["value"]
                
                if "messages" not in value:
                    continue
                    
                # Extract contact information
                phone_number = None
                name = None
                
                if "contacts" in value:
                    for contact in value["contacts"]:
                        if "wa_id" in contact:
                            phone_number = contact["wa_id"]
                            
                        if "profile" in contact and "name" in contact["profile"]:
                            name = contact["profile"]["name"]
                
                # Process each message
                for message in value["messages"]:
                    await process_message(db, menu_service, message, phone_number, name)
    except Exception as e:
        logger.error(f"Error processing webhook entries: {str(e)}")


async def process_message(
    db: Session, 
    menu_service: MenuService, 
    message: Dict[str, Any], 
    phone_number: Optional[str] = None, 
    name: Optional[str] = None
):
    """
    Process a single message from the webhook - simplified version
    """
    try:
        # Ensure we have a phone number
        if not phone_number and "from" in message:
            phone_number = message["from"]
            
        if not phone_number:
            logger.error("No phone number in message")
            return
            
        # Extract message text
        message_text = "No text"
        if message.get("type") == "text" and "text" in message:
            message_text = message["text"].get("body", "No text")
        
        # Log receipt of message
        logger.info(f"Received message: '{message_text}' from {phone_number}")
        
        # Check if user exists
        user = user_crud.get_by_phone_number(db, phone_number=phone_number)
        
        if not user:
            # Create new user
            logger.info(f"Creating new user with phone number {phone_number}")
            user = user_crud.create_with_phone(
                db,
                obj_in={
                    "phone_number": phone_number,
                    "name": name or "Usuário",
                    "terms_accepted": True  # Accept terms automatically for testing
                }
            )
        
        # Send a simple response
        await whatsapp_service.send_message(
            phone_number=phone_number,  # Use phone_number directly to avoid any attribute issues
            message=f"Olá! Recebi sua mensagem: '{message_text}'",
            log_to_db=False,  # Disable logging temporarily
            user_id=None,     # Don't require user_id for now
            db=None           # Don't require db for now
        )
        
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        # Print detailed traceback for debugging
        import traceback
        logger.error(traceback.format_exc())


async def send_terms_message(db: Session, user: User):
    """
    Send terms and conditions message
    """
    message = (
        "*Termos e Condições*\n\n"
        "Antes de começarmos, precisamos que você aceite nossos termos e condições de uso.\n\n"
        "Por favor, leia nossos termos em: https://example.com/terms\n\n"
        "Para continuar, selecione uma opção abaixo:"
    )
    
    buttons = [
        {"id": "accept_terms", "title": "Aceitar"},
        {"id": "reject_terms", "title": "Recusar"}
    ]
    
    await whatsapp_service.send_button_message(
        phone_number=user.phone_number,
        body_text=message,
        buttons=buttons,
        log_to_db=True,
        user_id=user.id,
        db=db
    )


async def send_outside_business_hours_message(db: Session, user: User):
    """
    Send message for outside business hours
    """
    start_hour = settings.BUSINESS_HOURS_START
    end_hour = settings.BUSINESS_HOURS_END
    
    message = (
        f"*Fora do Horário de Atendimento*\n\n"
        f"Olá! Nosso horário de atendimento é de {start_hour}h às {end_hour}h, de segunda a sexta-feira.\n\n"
        f"Sua mensagem foi registrada e responderemos assim que possível durante o próximo horário de atendimento.\n\n"
        f"Agradecemos sua compreensão."
    )
    
    await whatsapp_service.send_message(
        phone_number=user.phone_number,
        message=message,
        log_to_db=True,
        user_id=user.id,
        db=db
    )


async def send_response(db: Session, user: User, message: str, response_data: Dict[str, Any]):
    """
    Send response based on type
    """
    response_type = response_data.get("type", "text")
    
    if response_type == "text":
        await whatsapp_service.send_message(
            phone_number=user.phone_number,
            message=message,
            log_to_db=True,
            user_id=user.id,
            db=db
        )
    elif response_type == "button":
        await whatsapp_service.send_button_message(
            phone_number=user.phone_number,
            body_text=message,
            buttons=response_data.get("buttons", []),
            log_to_db=True,
            user_id=user.id,
            db=db
        )
    elif response_type == "list":
        await whatsapp_service.send_list_message(
            phone_number=user.phone_number,
            header_text=response_data.get("header", "Menu"),
            body_text=message,
            footer_text=response_data.get("footer", "Select an option"),
            button_text=response_data.get("button_text", "Click here"),
            sections=response_data.get("sections", []),
            log_to_db=True,
            user_id=user.id,
            db=db
        )
    elif response_type == "link":
        await whatsapp_service.send_link_message(
            phone_number=user.phone_number,
            title=response_data.get("title", "Link"),
            body_text=message,
            url=response_data.get("url", ""),
            button_text=response_data.get("button_text", "Click here"),
            log_to_db=True,
            user_id=user.id,
            db=db
        )
    else:
        # Default to text for unknown types
        await whatsapp_service.send_message(
            phone_number=user.phone_number,
            message=message,
            log_to_db=True,
            user_id=user.id,
            db=db
        )


def is_admin_user(user: User) -> bool:
    """
    Check if user is a system admin
    """
    # Implement admin check logic here
    # For example, check if user's phone number is in a list of admin numbers
    admin_numbers = os.getenv("ADMIN_PHONE_NUMBERS", "").split(",")
    return user.phone_number in admin_numbers