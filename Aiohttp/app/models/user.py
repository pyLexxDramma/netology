from passlib.context import CryptContext
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship  # Добавьте relationship
from sqlalchemy.sql import func

from app.db.database import Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Обратная связь к объявлениям
    advertisements = relationship("Advertisement", back_populates="owner")

    def set_password(self, password):
        self.hashed_password = pwd_context.hash(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.hashed_password)