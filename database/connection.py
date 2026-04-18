import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'condominio.db')
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    # Importar todos los modelos para que Base.metadata los reconozca
    import models.user
    import models.property
    import models.finance
    Base.metadata.create_all(bind=engine)

def get_session():
    return SessionLocal()
