from typing import Dict, Any, Optional
import time

# Simple in-memory session store
# In a production app, you might use Redis or another distributed cache
SESSION_STORE: Dict[str, Dict[str, Any]] = {}
SESSION_EXPIRY = 3600  # 1 hour in seconds

def create_session(session_id: str, data: Dict[str, Any]) -> None:
    """
    Create a new session
    """
    SESSION_STORE[session_id] = {
        "data": data,
        "created_at": time.time(),
        "last_accessed": time.time()
    }

def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """
    Get session data if exists and not expired
    """
    session = SESSION_STORE.get(session_id)
    if not session:
        return None
        
    # Check if session is expired
    if time.time() - session["last_accessed"] > SESSION_EXPIRY:
        delete_session(session_id)
        return None
        
    # Update last access time
    session["last_accessed"] = time.time()
    return session["data"]

def update_session(session_id: str, data: Dict[str, Any]) -> None:
    """
    Update session data
    """
    if session_id in SESSION_STORE:
        SESSION_STORE[session_id]["data"].update(data)
        SESSION_STORE[session_id]["last_accessed"] = time.time()

def delete_session(session_id: str) -> None:
    """
    Delete a session
    """
    if session_id in SESSION_STORE:
        del SESSION_STORE[session_id]

def clean_expired_sessions() -> None:
    """
    Remove all expired sessions
    """
    current_time = time.time()
    expired_sessions = [
        session_id for session_id, session in SESSION_STORE.items()
        if current_time - session["last_accessed"] > SESSION_EXPIRY
    ]
    
    for session_id in expired_sessions:
        delete_session(session_id)