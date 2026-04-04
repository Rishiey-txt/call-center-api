from sqlalchemy import Column, String, Float, DateTime, JSON
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

class Base(DeclarativeBase):
    pass

class CallLog(Base):
    __tablename__ = "call_logs"

    id          = Column(String, primary_key=True)
    created_at  = Column(DateTime, default=datetime.utcnow)
    language    = Column(String(10))
    transcript  = Column(String)
    summary     = Column(String)
    payment     = Column(String(20))
    rejection   = Column(String(30))
    sentiment   = Column(String(10))
    compliance  = Column(Float)
    adherence   = Column(String(15))
    raw_response = Column(JSON)
