from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.crud.menu import CRUDMenu, CRUDMenuState
from app.db.crud.user import CRUDUser, CRUDConversationLog
from app.models.menu import Menu, MenuState
from app.models.user import User
from app.services.whatsapp import whatsapp_service
from app.utils.constants import MenuType, MessageDirection
from config.settings import settings


class MenuService:
    def __init__(self, menu_crud: CRUDMenu, menu_state_crud: CRUDMenuState, user_crud: CRUDUser, log_crud: CRUDConversationLog):
        self.menu_crud = menu_crud
        self.menu_state_crud = menu_state_crud
        self.user_crud = user_crud
        self.log_crud = log_crud
        
    async def get_or_create_menu_state(self, db: Session, user_id: int) -> MenuState:
        """
        Get or create menu state for a user
        """
        menu_state = self.menu_state_crud.get_by_user_id(db, user_id=user_id)
        
        if not menu_state:
            # Create a new menu state
            menu_state = self.menu_state_crud.create(
                db,
                obj_in={
                    "user_id": user_id,
                    "current_menu": "initial",
                    "awaiting_response": False,
                    "form_filled": False,
                    "context_data": {}
                }
            )
            
        return menu_state
        
    async def get_menu_by_name(self, db: Session, menu_name: str) -> Optional[Menu]:
        """
        Get a menu by its name
        """
        return self.menu_crud.get_by_name(db, name=menu_name)
        
    async def handle_incoming_message(
        self, 
        db: Session, 
        user: User, 
        message_text: str,
        interactive_data: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Process incoming message and return appropriate response
        """
        # Get or create menu state for the user
        menu_state = await self.get_or_create_menu_state(db, user.id)
        
        # Log incoming message
        self.log_crud.create_log(
            db=db,
            user_id=user.id,
            message=message_text,
            direction=MessageDirection.INCOMING,
            menu_option=menu_state.current_menu
        )
        
        # If interactive data is present, process button/list selection
        if interactive_data and menu_state.awaiting_response:
            response_message, response_data = await self.process_interactive_response(
                db, 
                user, 
                menu_state, 
                interactive_data
            )
            return response_message, response_data
            
        # If we're awaiting a response for a form/prompt
        if menu_state.awaiting_response and not interactive_data:
            response_message, response_data = await self.process_form_response(
                db,
                user,
                menu_state,
                message_text
            )
            return response_message, response_data
            
        # Handle standard menu navigation
        current_menu = await self.get_menu_by_name(db, menu_state.current_menu)
        
        # If current menu not found, reset to initial menu
        if not current_menu:
            menu_state.current_menu = "initial"
            db.commit()
            current_menu = await self.get_menu_by_name(db, "initial")
            
        # Handle special keywords like "voltar" (back)
        if message_text.lower() in ["voltar", "back", "return"]:
            return await self.handle_back_navigation(db, user, menu_state)
            
        # Check if the message is a menu option
        if current_menu.options and message_text in current_menu.options:
            option = current_menu.options[message_text]
            next_menu_name = option.get("next_menu")
            
            if next_menu_name:
                next_menu = await self.get_menu_by_name(db, next_menu_name)
                if next_menu:
                    # Update menu state
                    menu_state.current_menu = next_menu_name
                    db.commit()
                    
                    # Return the content of the next menu
                    return await self.format_menu_response(db, user, next_menu)
        
        # If no specific handling, return current menu content
        return await self.format_menu_response(db, user, current_menu)
        
    async def handle_back_navigation(
        self, 
        db: Session, 
        user: User, 
        menu_state: MenuState
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Handle back navigation request
        """
        current_menu = await self.get_menu_by_name(db, menu_state.current_menu)
        
        if not current_menu or not current_menu.parent_id:
            # If no parent, go to initial menu
            initial_menu = await self.get_menu_by_name(db, "initial")
            menu_state.current_menu = "initial"
            db.commit()
            return await self.format_menu_response(db, user, initial_menu)
            
        # Get parent menu
        parent_menu = self.menu_crud.get(db, current_menu.parent_id)
        menu_state.current_menu = parent_menu.name
        db.commit()
        
        return await self.format_menu_response(db, user, parent_menu)
        
    async def process_interactive_response(
        self,
        db: Session,
        user: User,
        menu_state: MenuState,
        interactive_data: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Process responses from interactive messages (buttons/lists)
        """
        selection_id = None
        
        # Extract selection ID from different types of interactive messages
        if "button_reply" in interactive_data:
            selection_id = interactive_data["button_reply"]["id"]
        elif "list_reply" in interactive_data:
            selection_id = interactive_data["list_reply"]["id"]
            
        if not selection_id:
            # Invalid interactive data
            return "Sorry, I couldn't process your selection. Please try again.", {}
            
        # Log the selection
        self.log_crud.create_log(
            db=db,
            user_id=user.id,
            message=f"Selected option: {selection_id}",
            direction=MessageDirection.INCOMING,
            menu_option=menu_state.current_menu
        )
        
        # Get current menu
        current_menu = await self.get_menu_by_name(db, menu_state.current_menu)
        
        # Process based on the context of the menu
        if current_menu and current_menu.options:
            options_data = current_menu.options
            
            # Find the selected option
            for option_key, option_data in options_data.items():
                if option_data.get("id") == selection_id:
                    # Handle the option based on its type
                    if "next_menu" in option_data:
                        next_menu_name = option_data["next_menu"]
                        next_menu = await self.get_menu_by_name(db, next_menu_name)
                        
                        if next_menu:
                            # Update menu state
                            menu_state.current_menu = next_menu_name
                            menu_state.awaiting_response = False
                            
                            # Save any context data if needed
                            if "context" in option_data:
                                if not menu_state.context_data:
                                    menu_state.context_data = {}
                                menu_state.context_data.update(option_data["context"])
                                
                            db.commit()
                            
                            # Return the content of the next menu
                            return await self.format_menu_response(db, user, next_menu)
                    
                    # Handle action options
                    if "action" in option_data:
                        action = option_data["action"]
                        
                        # Execute specific actions like accept_terms, etc.
                        if action == "accept_terms":
                            user.terms_accepted = True
                            db.commit()
                            
                            # After accepting terms, go to initial menu
                            initial_menu = await self.get_menu_by_name(db, "initial")
                            menu_state.current_menu = "initial"
                            menu_state.awaiting_response = False
                            db.commit()
                            
                            return await self.format_menu_response(db, user, initial_menu)
        
        # Default response if nothing specific matched
        return "I'm sorry, I couldn't process that selection properly. Let me take you back to the main menu.", {
            "type": "text"
        }
        
    async def process_form_response(
        self,
        db: Session,
        user: User,
        menu_state: MenuState,
        message_text: str
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Process form responses when awaiting user input
        """
        # Get the current menu context
        current_menu = await self.get_menu_by_name(db, menu_state.current_menu)
        
        # Initialize context if not present
        if not menu_state.context_data:
            menu_state.context_data = {}
            
        # Get the form field we're waiting for
        awaiting_field = menu_state.context_data.get("awaiting_field")
        
        if awaiting_field:
            # Store the response in context
            menu_state.context_data[awaiting_field] = message_text
            
            # Check if we're completing a multi-field form
            form_fields = menu_state.context_data.get("form_fields", [])
            
            if form_fields and awaiting_field in form_fields:
                # Get index of current field
                current_index = form_fields.index(awaiting_field)
                
                # If there are more fields to collect
                if current_index < len(form_fields) - 1:
                    next_field = form_fields[current_index + 1]
                    field_prompt = menu_state.context_data.get(f"{next_field}_prompt", f"Please enter {next_field}:")
                    
                    # Update awaiting field
                    menu_state.context_data["awaiting_field"] = next_field
                    db.commit()
                    
                    return field_prompt, {"type": "text"}
                else:
                    # Form is complete
                    menu_state.form_filled = True
                    menu_state.awaiting_response = False
                    
                    # Get next menu after form completion
                    next_menu_name = menu_state.context_data.get("next_menu_after_form", "initial")
                    next_menu = await self.get_menu_by_name(db, next_menu_name)
                    
                    menu_state.current_menu = next_menu_name
                    db.commit()
                    
                    # Process form submission if defined
                    if "form_handler" in menu_state.context_data:
                        form_handler = menu_state.context_data["form_handler"]
                        # ... implement form handlers for different forms
                        
                    return await self.format_menu_response(db, user, next_menu)
            
            # Single field response
            next_menu_name = menu_state.context_data.get("next_menu", "initial")
            next_menu = await self.get_menu_by_name(db, next_menu_name)
            
            menu_state.current_menu = next_menu_name
            menu_state.awaiting_response = False
            db.commit()
            
            return await self.format_menu_response(db, user, next_menu)
            
        # Default fallback if no specific awaiting field
        menu_state.awaiting_response = False
        db.commit()
        
        return await self.format_menu_response(db, user, current_menu)
        
    async def format_menu_response(
        self, 
        db: Session, 
        user: User, 
        menu: Menu
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Format a menu response based on its type
        """
        if not menu:
            # Fallback to initial menu if menu not found
            initial_menu = await self.get_menu_by_name(db, "initial")
            return await self.format_menu_response(db, user, initial_menu)
            
        # Format content with user's name
        content = menu.content.replace("{name}", user.name or "")
            
        # Determine menu type based on options
        if not menu.options:
            # Simple text menu
            return content, {"type": "text"}
            
        menu_type = menu.options.get("menu_type", MenuType.TEXT)
        
        if menu_type == MenuType.BUTTON:
            # Button menu
            buttons = []
            for button_id, button_data in menu.options.get("buttons", {}).items():
                buttons.append({
                    "id": button_id,
                    "title": button_data.get("title", button_id)
                })
                
            return content, {
                "type": "button",
                "buttons": buttons
            }
            
        elif menu_type == MenuType.LIST:
            # List menu
            header = menu.options.get("header", "Menu")
            footer = menu.options.get("footer", "Select an option")
            button_text = menu.options.get("button_text", "Click here")
            sections = []
            
            for section_id, section_data in menu.options.get("sections", {}).items():
                rows = []
                
                for row_id, row_data in section_data.get("rows", {}).items():
                    rows.append({
                        "id": row_id,
                        "title": row_data.get("title", row_id),
                        "description": row_data.get("description", "")
                    })
                    
                if rows:
                    sections.append({
                        "title": section_data.get("title", section_id),
                        "rows": rows
                    })
                    
            return content, {
                "type": "list",
                "header": header,
                "footer": footer,
                "button_text": button_text,
                "sections": sections
            }
            
        elif menu_type == MenuType.LINK:
            # Link message
            url = menu.options.get("url", "")
            title = menu.options.get("title", "Link")
            button_text = menu.options.get("button_text", "Click here")
            
            return content, {
                "type": "link",
                "url": url,
                "title": title,
                "button_text": button_text
            }
            
        # Default to text if unknown type
        return content, {"type": "text"}