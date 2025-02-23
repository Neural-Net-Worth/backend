from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from models import Base
from models.user import User


class RedeemedRewards(Base):
    __tablename__ = 'redeemed_rewards'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    reward_name = Column(String, index=True)
    reward_amount = Column(Float)
    needed_points = Column(Integer)
    redeemed_at = Column(String)

    user = relationship("User", back_populates="redeemed_rewards")
