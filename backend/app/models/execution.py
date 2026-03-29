from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Execution(Base):
    __tablename__ = "execution"

    id = Column(Integer, primary_key=True, index=True)
    idea_id = Column(Integer, ForeignKey("ideas.id"), unique=True, nullable=False)
    mvp_plan = Column(Text)
    stack = Column(Text)
    monetization = Column(Text)
    estimated_days = Column(Integer)
    status = Column(String(20), default="pending")  # pending, building, launched

    idea = relationship("Idea", back_populates="execution")
