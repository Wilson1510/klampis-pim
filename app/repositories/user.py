from .base import CRUDBase
from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate, User

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    pass

user = CRUDUser(User)