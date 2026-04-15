from sqlalchemy import Column, String, Float, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from uuid6 import uuid7

Base = declarative_base()


class DemographicProfile(Base):
    __tablename__ = "demographic_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid7()))
    name = Column(String(255), unique=True, nullable=False, index=True)
    gender = Column(String(50), nullable=True)
    gender_probability = Column(Float, nullable=True)
    sample_size = Column(Integer, nullable=True)
    age = Column(Integer, nullable=True)
    age_group = Column(String(20), nullable=True, index=True)
    country_id = Column(String(10), nullable=True, index=True)
    country_probability = Column(Float, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.utcnow(), nullable=False)

    def __repr__(self):
        return f"<DemographicProfile(name={self.name}, gender={self.gender}, age={self.age})>"
