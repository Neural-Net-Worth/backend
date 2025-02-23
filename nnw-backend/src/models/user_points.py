# models/rewards_points.py
from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from models import Base
from models.user import User


class UserPoints(Base):
    __tablename__ = 'user_points'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'),
                     nullable=False, unique=True)
    points = Column(Float, default=0)

    user = relationship("User", back_populates="user_points")
