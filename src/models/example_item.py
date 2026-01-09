from sqlalchemy import Column, Integer, String, DateTime, func
from models.base import Base

class ExampleItem(Base):
    __tablename__ = "example_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
