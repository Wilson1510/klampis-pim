from .base import CRUDBase
from ..models.user import Users
from ..schemas.user import UserCreate, UserUpdate, User


class CRUDUser(CRUDBase[Users, UserCreate, UserUpdate]):
    pass

user = CRUDUser(Users)
