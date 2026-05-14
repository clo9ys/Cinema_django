from sqlalchemy import Column, Integer, String, Text
from search_service.core.database import Base

class MovieModel(Base):
    __tablename__ = "movies_movie"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), index=True)
    summary = Column(Text)
    release_year = Column(Integer)
    duration_minutes = Column(Integer)
    age_limit = Column(Integer)