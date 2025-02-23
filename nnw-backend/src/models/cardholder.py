from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from models import Base


class Cardholder(Base):
    __tablename__ = "cardholders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    cardholder_id = Column(String, unique=True, index=True, nullable=False)
    provider = Column(String, nullable=False)

    user = relationship("User", back_populates="cardholders")
