from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from models import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    refresh_tokens = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan")
    profile = relationship("Profile", back_populates="user",
                           uselist=False, cascade="all, delete-orphan")
    cardholders = relationship(
        "Cardholder", back_populates="user", cascade="all, delete-orphan")

    user_points = relationship(
        "UserPoints", back_populates="user", cascade="all, delete-orphan")

    redeemed_rewards = relationship(
        "RedeemedRewards", back_populates="user", cascade="all, delete-orphan")
    cardholders = relationship(
        "Cardholder", back_populates="user", cascade="all, delete-orphan")
