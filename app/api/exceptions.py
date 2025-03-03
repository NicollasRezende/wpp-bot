from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

class WhatsAppError(Exception):
    """Base exception for WhatsApp API errors"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class DatabaseError(Exception):
    """Exception for database errors"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

async def whatsapp_exception_handler(request: Request, exc: WhatsAppError):
    """Handle WhatsAppError exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )

async def database_exception_handler(request: Request, exc: DatabaseError):
    """Handle DatabaseError exceptions"""
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": f"Database error: {exc.message}"},
    )

def add_exception_handlers(app):
    """Add all exception handlers to the app"""
    app.add_exception_handler(WhatsAppError, whatsapp_exception_handler)
    app.add_exception_handler(DatabaseError, database_exception_handler)