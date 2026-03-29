from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Analysis(Base):
    __tablename__ = "analysis"

    id = Column(Integer, primary_key=True, index=True)
    idea_id = Column(Integer, ForeignKey("ideas.id"), unique=True, nullable=False)
    problem = Column(Text)
    failure_type = Column(String(50))  # timing, technology, execution, market
    current_opportunity = Column(String(20))  # alta, media, baja
    pain_score = Column(Integer)  # 1-5
    paying_capacity = Column(Integer)  # 1-5
    mvp_ease = Column(Integer)  # 1-5
    tech_advantage = Column(Integer)  # 1-5
    total_score = Column(Float)

    idea = relationship("Idea", back_populates="analysis")
