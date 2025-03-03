from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from config.database import get_db
from app.db.crud.user import user as user_crud
from app.schemas.user import User, UserCreate, UserUpdate
from app.services.logger import logger

router = APIRouter()

@router.get("/users", response_model=List[User])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve users.
    """
    users = user_crud.get_multi(db, skip=skip, limit=limit)
    return users

@router.post("/users", response_model=User)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Create new user.
    """
    user = user_crud.get_by_phone_number(db, phone_number=user_in.phone_number)
    if user:
        raise HTTPException(
            status_code=400,
            detail="A user with this phone number already exists."
        )
    return user_crud.create(db, obj_in=user_in)

@router.get("/users/{user_id}", response_model=User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get a specific user by id.
    """
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, user_in: UserUpdate, db: Session = Depends(get_db)):
    """
    Update a user.
    """
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user = user_crud.update(db, db_obj=user, obj_in=user_in)
    return user

@router.delete("/users/{user_id}", response_model=User)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete a user.
    """
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user = user_crud.remove(db, id=user_id)
    return user