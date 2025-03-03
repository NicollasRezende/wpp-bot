from enum import Enum, auto


class MenuType(str, Enum):
    """Types of menus that can be displayed"""
    TEXT = "text"
    BUTTON = "button"
    LIST = "list"
    LINK = "link"
    TEMPLATE = "template"
    MEDIA = "media"
    LOCATION = "location"
    CONTACT = "contact"


class MessageDirection(str, Enum):
    """Direction of messages in conversation log"""
    INCOMING = "incoming"
    OUTGOING = "outgoing"


class BusinessHours:
    """Default business hours"""
    START = 8  # 8 AM
    END = 18   # 6 PM


class GreetingWords:
    """Common greeting words to trigger initial menu"""
    GREETINGS = [
        "olá",
        "ola",
        "oi",
        "e aí",
        "e ai",
        "tudo bem",
        "bom dia",
        "boa tarde",
        "boa noite",
        "hello",
        "hi",
        "hey",
        "eae",
        "salve"
    ]


class NavigationCommands:
    """Common navigation commands"""
    BACK = ["voltar", "back", "return", "retornar"]
    HOME = ["inicio", "menu", "home", "principal", "main"]
    HELP = ["ajuda", "help", "socorro", "auxilio"]
    EXIT = ["sair", "exit", "encerrar", "finalizar"]