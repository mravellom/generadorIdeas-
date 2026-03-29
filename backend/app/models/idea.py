from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Idea(Base):
    __tablename__ = "ideas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    failure_reason = Column(Text)
    industry = Column(String(100))
    year = Column(Integer)
    source_url = Column(String(500))

    analysis = relationship("Analysis", back_populates="idea", uselist=False)
    execution = relationship("Execution", back_populates="idea", uselist=False)
