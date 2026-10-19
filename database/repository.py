import hashlib
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from database.models import Lead


def _normalize_domain(website: str) -> Optional[str]:
    if not website:
        return None
    try:
        from urllib.parse import urlparse
        parsed = urlparse(website if '://' in website else f'https://{website}')
        domain = parsed.netloc.lower()
        # Remove www.
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except:
        return None


def _normalize_email(email: str) -> Optional[str]:
    if not email:
        return None
    return email.strip().lower()


def _normalize_phone(phone: str) -> Optional[str]:
    if not phone:
        return None
    # Simple digit extraction
    import re
    digits = re.sub(r'\D', '', phone)
    return digits if digits else None


def lead_hash(lead_data: Dict[str, Any]) -> str:
    """Create deterministic hash for deduplication."""
    components = []
    if lead_data.get('google_place_id'):
        components.append(f"place:{lead_data['google_place_id']}")
    domain = _normalize_domain(lead_data.get('website') or '')
    if domain:
        components.append(f"domain:{domain}")
    email = _normalize_email(lead_data.get('email') or '')
    if email:
        components.append(f"email:{email}")
    phone = _normalize_phone(lead_data.get('phone') or '')
    if phone:
        components.append(f"phone:{phone}")
    if lead_data.get('business_name') and lead_data.get('address'):
        name = lead_data['business_name'].strip().lower()
        addr = lead_data['address'].strip().lower()
        components.append(f"nameaddr:{hashlib.md5((name+addr).encode()).hexdigest()}")
    if not components:
        components.append(str(datetime.utcnow()))
    return hashlib.md5('|'.join(components).encode()).hexdigest()


class LeadRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def find_duplicate(self, lead_data: Dict[str, Any]) -> Optional[Lead]:
        """Find duplicate lead using priority keys."""
        # 1. Google Place ID
        if lead_data.get('google_place_id'):
            q = self.db.query(Lead).filter(Lead.google_place_id == lead_data['google_place_id']).first()
            if q:
                return q
        # 2. Domain
        domain = _normalize_domain(lead_data.get('website') or '')
        if domain:
            q = self.db.query(Lead).filter(Lead.domain == domain).first()
            if q:
                return q
        # 3. Email
        email = _normalize_email(lead_data.get('email') or '')
        if email:
            q = self.db.query(Lead).filter(Lead.email == email).first()
            if q:
                return q
        # 4. Phone
        phone = _normalize_phone(lead_data.get('phone') or '')
        if phone:
            q = self.db.query(Lead).filter(Lead.phone == phone).first()
            if q:
                return q
        return None
    
    def create_or_update(self, lead_data: Dict[str, Any]) -> tuple[Lead, bool]:
        """Create lead or update if duplicate found. Returns (lead, is_new)."""
        dup = self.find_duplicate(lead_data)
        if dup:
            # Update existing
            for k, v in lead_data.items():
                if hasattr(dup, k) and v is not None:
                    setattr(dup, k, v)
            dup.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(dup)
            return dup, False
        else:
            # Create new
            lead = Lead(**lead_data)
            if not lead.lead_id:
                lead.lead_id = lead_hash(lead_data)
            self.db.add(lead)
            self.db.commit()
            self.db.refresh(lead)
            return lead, True
    
    def get_by_id(self, lead_id: str) -> Optional[Lead]:
        return self.db.query(Lead).filter(Lead.lead_id == lead_id).first()

    def get_by_pk(self, pk_id: int) -> Optional[Lead]:
        return self.db.query(Lead).filter(Lead.id == pk_id).first()
    
    def list_leads(self, limit: int = 100, offset: int = 0, **filters) -> List[Lead]:
        q = self.db.query(Lead)
        for k, v in filters.items():
            if hasattr(Lead, k) and v is not None:
                q = q.filter(getattr(Lead, k) == v)
        return q.order_by(Lead.created_at.desc()).offset(offset).limit(limit).all()

    def count(self, **filters) -> int:
        q = self.db.query(Lead)
        for k, v in filters.items():
            if hasattr(Lead, k) and v is not None:
                q = q.filter(getattr(Lead, k) == v)
        return q.count()

    def get_metrics(self) -> Dict[str, Any]:
        total = self.db.query(Lead).count()
        high_score = self.db.query(Lead).filter(Lead.lead_score >= 80).count()
        ready_outreach = self.db.query(Lead).filter(Lead.approved == True, Lead.email_status != 'sent').count()
        sent = self.db.query(Lead).filter(Lead.email_status == 'sent').count()
        pending_review = self.db.query(Lead).filter(
            Lead.generated_email.isnot(None),
            (Lead.approved == False) | (Lead.approved.is_(None))
        ).count()
        return {
            "total_leads": total,
            "high_score": high_score,
            "ready_outreach": ready_outreach,
            "emails_sent": sent,
            "pending_review": pending_review
        }

    def update_lead(self, lead_id: str, updates: Dict[str, Any]) -> Optional[Lead]:
        lead = self.get_by_id(lead_id)
        if not lead:
            return None
        for k, v in updates.items():
            if hasattr(lead, k):
                setattr(lead, k, v)
        lead.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(lead)
        return lead

    def delete_lead(self, pk_id: int) -> bool:
        lead = self.get_by_pk(pk_id)
        if not lead:
            return False
        self.db.delete(lead)
        self.db.commit()
        return True

