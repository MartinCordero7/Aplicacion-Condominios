from sqlalchemy import Column, Integer, String, Boolean
from models.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    full_name = Column(String(100))
    role = Column(String(20), default="Operativo") # Roles: Administrador, Contador, Operativo
    is_active = Column(Boolean, default=True)
