from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import SQLAlchemyError

from app.db.crud.base import CRUDBase
from app.models.menu import Menu, MenuState
from app.schemas.menu import MenuCreate, MenuUpdate, MenuStateCreate, MenuStateUpdate


class CRUDMenu(CRUDBase[Menu, MenuCreate, MenuUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Menu]:
        """
        Get a menu by name.
        """
        return db.query(Menu).filter(Menu.name == name).first()
    
    def get_active_menus(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Menu]:
        """
        Get active menus.
        """
        return db.query(Menu).filter(Menu.is_active == True).offset(skip).limit(limit).all()
    
    def get_menu_with_submenus(self, db: Session, *, menu_id: int) -> Optional[Menu]:
        """
        Get a menu with its submenus.
        """
        return db.query(Menu).options(
            selectinload(Menu.submenus)
        ).filter(Menu.id == menu_id).first()
    
    def get_root_menus(self, db: Session) -> List[Menu]:
        """
        Get all root menus (menus without a parent).
        """
        return db.query(Menu).filter(Menu.parent_id == None).all()


class CRUDMenuState(CRUDBase[MenuState, MenuStateCreate, MenuStateUpdate]):
    def get_by_user_id(self, db: Session, *, user_id: int) -> Optional[MenuState]:
        """
        Get menu state for a specific user.
        """
        return db.query(MenuState).filter(MenuState.user_id == user_id).first()