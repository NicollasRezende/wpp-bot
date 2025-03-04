from typing import Optional, List
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import SQLAlchemyError

from app.db.crud.base import CRUDBase
from app.models.user import User, ConversationLog
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_phone_number(self, db: Session, *, phone_number: str) -> Optional[User]:
        """
        Get a user by phone number.
        """
        return db.query(User).filter(User.phone_number == phone_number).first()
    
    def create_with_phone(self, db: Session, *, obj_in: dict) -> User:
        """
        Create a new user with phone number.
        """
        db_obj = User(
            name=obj_in.get("name"),
            phone_number=obj_in.get("phone_number"),
            contract_number=obj_in.get("contract_number"),
            terms_accepted=obj_in.get("terms_accepted", False)
        )
        db.add(db_obj)
        try:
            db.commit()
            db.refresh(db_obj)
        except SQLAlchemyError as e:
            db.rollback()
            raise e
        return db_obj
    
    def update_terms_acceptance(self, db: Session, *, phone_number: str, accepted: bool) -> Optional[User]:
        """
        Update the terms acceptance status for a user.
        """
        user = self.get_by_phone_number(db, phone_number=phone_number)
        if not user:
            return None
            
        user.terms_accepted = accepted
        db.add(user)
        try:
            db.commit()
            db.refresh(user)
        except SQLAlchemyError as e:
            db.rollback()
            raise e
        return user
    
    def get_users_with_logs(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get users with their conversation logs.
        """
        return db.query(User).options(
            selectinload(User.conversation_logs) #nao definido
        ).offset(skip).limit(limit).all()


class CRUDConversationLog(CRUDBase[ConversationLog, None, None]):
    def create_log(
        self, db: Session, *, user_id: int, message: str, direction: str, menu_option: Optional[str] = None
    ) -> ConversationLog:
        """
        Create a new conversation log entry.
        """
        db_obj = ConversationLog(
            user_id=user_id,
            message=message,
            direction=direction,
            menu_option=menu_option
        )
        db.add(db_obj)
        try:
            db.commit()
            db.refresh(db_obj)
        except SQLAlchemyError as e:
            db.rollback()
            raise e
        return db_obj
    
    def get_user_logs(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[ConversationLog]:
        """
        Get conversation logs for a specific user.
        """
        return db.query(ConversationLog).filter(
            ConversationLog.user_id == user_id
        ).order_by(ConversationLog.timestamp.desc()).offset(skip).limit(limit).all()


# Create CRUD instances
user = CRUDUser(User)
conversation_log = CRUDConversationLog(ConversationLog)