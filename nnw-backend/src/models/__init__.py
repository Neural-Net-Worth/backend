from config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = settings.database_url

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db():
    from models.user import User
    from models.refresh_token import RefreshToken
    from models.profile import Profile
    Base.metadata.create_all(bind=engine)
