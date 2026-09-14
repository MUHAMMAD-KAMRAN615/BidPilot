import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Text, DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from database.connection import Base

class CompanyProfile(Base):
    __tablename__ = "company_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    ein_tax_id = Column(String(64), unique=True, nullable=False)
    annual_revenue = Column(Numeric(15, 2), nullable=False)
    employee_count = Column(Integer, nullable=False)
    security_clearance = Column(String(100), nullable=True)
    certifications = Column(JSONB, default=list)
    core_competencies = Column(JSONB, default=list)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    analyses = relationship("TenderAnalysis", back_populates="company_profile")

class Tender(Base):
    __tablename__ = "tenders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(512), nullable=False)
    issuing_authority = Column(String(255), nullable=True)
    document_hash = Column(String(64), unique=True, nullable=False)
    file_path = Column(String(1024), nullable=False)
    estimated_budget = Column(Numeric(15, 2), nullable=True)
    submission_deadline = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    analyses = relationship("TenderAnalysis", back_populates="tender")

class TenderAnalysis(Base):
    __tablename__ = "tender_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tender_id = Column(UUID(as_uuid=True), ForeignKey("tenders.id"), nullable=False)
    company_profile_id = Column(UUID(as_uuid=True), ForeignKey("company_profiles.id"), nullable=False)
    
    bid_decision = Column(String(16), nullable=False)
    bid_score = Column(Float, nullable=False)
    summary = Column(Text, nullable=False)
    
    eligibility_results = Column(JSONB, default=dict)
    compliance_results = Column(JSONB, default=dict)
    risk_results = Column(JSONB, default=dict)
    
    proposal_draft = Column(Text, nullable=True)
    submission_checklist = Column(JSONB, nullable=True)
    status = Column(String(32), default="PROCESSING")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    tender = relationship("Tender", back_populates="analyses")
    company_profile = relationship("CompanyProfile", back_populates="analyses")
