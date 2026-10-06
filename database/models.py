from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, JSON
from core.database import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(String(50), unique=True, index=True)
    
    # Basic business info
    business_name = Column(String(255), index=True)
    business_category = Column(String(100))
    industry = Column(String(100), index=True)
    country = Column(String(100), index=True)
    state = Column(String(100))
    city = Column(String(100), index=True)
    postal_code = Column(String(50))
    address = Column(Text)
    phone = Column(String(50))
    email = Column(String(255), index=True)
    website = Column(String(500))
    domain = Column(String(255), index=True)
    google_place_id = Column(String(255), unique=True, index=True)
    google_maps_url = Column(String(500))
    rating = Column(Float)
    review_count = Column(Integer)
    hours = Column(Text)
    
    # Social links
    facebook_url = Column(String(500))
    instagram_url = Column(String(500))
    linkedin_url = Column(String(500))
    
    # Source
    source = Column(String(100))
    source_id = Column(String(255))
    scraped_at = Column(DateTime, default=datetime.utcnow)
    
    # Website intelligence
    website_status = Column(String(50))
    website_title = Column(String(500))
    website_description = Column(Text)
    website_platform = Column(String(100))
    technology_stack = Column(JSON)
    ssl_enabled = Column(Boolean)
    mobile_friendly = Column(Boolean)
    analytics_detected = Column(Boolean)
    google_tag_manager = Column(Boolean)
    meta_pixel = Column(Boolean)
    booking_system = Column(String(100))
    chatbot_detected = Column(Boolean)
    whatsapp_detected = Column(Boolean)
    ecommerce_detected = Column(Boolean)
    ecommerce_platform = Column(String(100))
    
    # Business intelligence
    business_type = Column(String(100))
    business_size_estimate = Column(String(50))
    digital_presence_score = Column(Integer)
    website_score = Column(Integer)
    local_presence_score = Column(Integer)
    automation_score = Column(Integer)
    
    # Opportunity
    primary_opportunity = Column(String(200))
    secondary_opportunities = Column(JSON)
    opportunity_reason = Column(Text)
    
    # Scoring
    lead_score = Column(Integer, index=True)
    score_breakdown = Column(JSON)
    outreach_confidence = Column(Float)
    
    # Outreach
    contact_status = Column(String(50), default="new")
    email_status = Column(String(50), default="pending")
    campaign = Column(String(100))
    generated_subject = Column(String(500))
    generated_email = Column(Text)
    approved = Column(Boolean, default=False)
    sent_at = Column(DateTime)
    reply_status = Column(String(50), default="none")
    followup_status = Column(String(50), default="none")
    unsubscribe = Column(Boolean, default=False)
    do_not_contact = Column(Boolean, default=False)
    suppression_reason = Column(String(255))
    suppressed_at = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    pipeline_status = Column(String(50), default="DISCOVERED")
    audit_trail = Column(JSON)
