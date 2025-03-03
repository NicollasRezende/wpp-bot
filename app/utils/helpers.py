import os
import random
import string
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
import pytz
from pathlib import Path

from config.settings import settings
from app.utils.constants import GreetingWords, BusinessHours


def is_greeting(message: str) -> bool:
    """
    Check if a message is a greeting
    """
    message = message.lower().strip().strip('!.,;:')
    return message in GreetingWords.GREETINGS


def generate_random_code(length: int = 10) -> str:
    """
    Generate a random alphanumeric code
    """
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def generate_contract_number() -> str:
    """
    Generate a unique contract number
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = ''.join(random.choices(string.digits, k=4))
    return f"CNT-{timestamp}-{random_suffix}"


def is_business_hours() -> bool:
    """
    Check if current time is within business hours
    """
    tz = pytz.timezone(settings.TIMEZONE)
    now = datetime.now(tz)
    
    # Check if it's weekend (5 = Saturday, 6 = Sunday)
    if now.weekday() >= 5:
        return False
        
    # Check if current hour is within business hours
    hour = now.hour
    return settings.BUSINESS_HOURS_START <= hour < settings.BUSINESS_HOURS_END


def format_phone_number(phone: str) -> str:
    """
    Format phone number for consistent storage
    """
    # Remove all non-digit characters
    digits_only = ''.join(filter(str.isdigit, phone))
    
    # Ensure it has international format (+XX)
    if not digits_only.startswith('55') and len(digits_only) <= 11:
        digits_only = '55' + digits_only
        
    return digits_only


def log_to_file(phone_number: str, name: str, message: str, menu_option: Optional[str] = None) -> None:
    """
    Log conversation to a file
    """
    log_dir = Path(settings.LOG_PATH)
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = log_dir / f"{phone_number}_log.txt"
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    entry = f"\n{'-'*50}\n"
    entry += f"Timestamp: {timestamp}\n"
    entry += f"From: {name} ({phone_number})\n"
    entry += f"Message: {message}\n"
    
    if menu_option:
        entry += f"Menu: {menu_option}\n"
        
    entry += f"{'-'*50}\n"
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(entry)


def load_menu_templates() -> Dict[str, Any]:
    """
    Load menu templates from JSON file
    """
    menu_file = Path(settings.BASE_DIR) / "app" / "utils" / "menu_templates.json"
    
    if not menu_file.exists():
        return {}
        
    with open(menu_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def replace_placeholders(text: str, replacements: Dict[str, str]) -> str:
    """
    Replace placeholders in text with values from a dictionary
    """
    for key, value in replacements.items():
        placeholder = "{" + key + "}"
        text = text.replace(placeholder, str(value))
        
    return text