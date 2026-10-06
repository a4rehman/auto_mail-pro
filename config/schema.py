from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class DiscoveryParams(BaseModel):
    country: str = Field(default="USA")
    state: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    industry: str = Field(default="local_business")
    keyword: Optional[str] = None
    min_rating: Optional[float] = None
    min_reviews: Optional[int] = None
    website_required: bool = True
    email_required: bool = False
    max_results: int = Field(default=50, ge=1, le=1000)


class LeadBase(BaseModel):
    business_name: str
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: str = "USA"
    industry: Optional[str] = None
    source: str = "apify"
