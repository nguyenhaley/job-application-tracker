from sqlalchemy import Column, Date, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    industry = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    role_title = Column(String(255), nullable=False)
    source = Column(String(100))
    date_applied = Column(Date, nullable=False)
    current_status = Column(String(50), default="applied")
    created_at = Column(DateTime, server_default=func.now())

    company = relationship("Company")

class StatusHistory(Base):
    __tablename__ = "status_history"

    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    status = Column(String(50), nullable=False)
    changed_at = Column(DateTime, server_default=func.now())

    application = relationship("Application")
