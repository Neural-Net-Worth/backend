from nnw_backend.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = settings.database_url

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db():
    from nnw_backend.models.user import User
    from nnw_backend.models.refresh_token import RefreshToken
    Base.metadata.create_all(bind=engine)
