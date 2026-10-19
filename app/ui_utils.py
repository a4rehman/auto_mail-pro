"""
UI Utilities & Shared Components for 100Solutionz Lead Intelligence Platform
"""
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
import streamlit as st

# Add project root to sys.path
ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.database import SessionLocal, init_db
from database.models import Lead
from database.repository import LeadRepository
from config.settings import settings


CUSTOM_CSS = """
<style>
/* Modern styling tokens */
:root {
    --primary: #4F46E5;
    --primary-light: #6366F1;
    --success: #10B981;
    --warning: #F59E0B;
    --danger: #EF4444;
}

/* Metric card styling */
div[data-testid="metric-container"] {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 14px 18px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

/* Badge styling */
.badge-score-high {
    background-color: rgba(16, 185, 129, 0.2);
    color: #10B981;
    padding: 3px 10px;
    border-radius: 12px;
    font-weight: 600;
    font-size: 0.85rem;
    border: 1px solid rgba(16, 185, 129, 0.4);
}
.badge-score-mid {
    background-color: rgba(245, 158, 11, 0.2);
    color: #F59E0B;
    padding: 3px 10px;
    border-radius: 12px;
    font-weight: 600;
    font-size: 0.85rem;
    border: 1px solid rgba(245, 158, 11, 0.4);
}
.badge-score-low {
    background-color: rgba(239, 68, 68, 0.2);
    color: #EF4444;
    padding: 3px 10px;
    border-radius: 12px;
    font-weight: 600;
    font-size: 0.85rem;
    border: 1px solid rgba(239, 68, 68, 0.4);
}

.tech-tag {
    display: inline-block;
    background: rgba(99, 102, 241, 0.15);
    color: #818CF8;
    border: 1px solid rgba(99, 102, 241, 0.3);
    padding: 2px 8px;
    margin: 2px 4px 2px 0;
    border-radius: 6px;
    font-size: 0.78rem;
    font-weight: 500;
}

/* Clean cards */
.lead-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 12px;
}

.system-pill {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.78rem;
    margin-right: 8px;
    font-weight: 500;
}
.pill-active {
    background: rgba(16, 185, 129, 0.15);
    color: #10B981;
    border: 1px solid rgba(16, 185, 129, 0.3);
}
.pill-dry {
    background: rgba(245, 158, 11, 0.15);
    color: #F59E0B;
    border: 1px solid rgba(245, 158, 11, 0.3);
}
.pill-neutral {
    background: rgba(99, 102, 241, 0.15);
    color: #818CF8;
    border: 1px solid rgba(99, 102, 241, 0.3);
}
</style>
"""


def init_page(page_title: str, page_icon: str = "🎯", show_header: bool = True):
    """Common page initialization with styling and header."""
    init_db()
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("### 🏢 **100Solutionz**")
        st.caption("B2B Lead Intelligence Platform")
        
        # System status indicators
        dry_label = "🛡️ DRY RUN (Safe)" if settings.DRY_RUN else "🚀 LIVE SMTP"
        dry_class = "pill-dry" if settings.DRY_RUN else "pill-active"
        
        st.markdown(f"""
        <div style="margin-bottom: 12px;">
            <span class="system-pill pill-active">🟢 DB Connected</span>
            <span class="system-pill {dry_class}">{dry_label}</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()

    if show_header:
        st.title(f"{page_icon} {page_title}")


def get_db():
    """Provides a fresh database session."""
    return SessionLocal()


def render_score_badge(score: Optional[int]) -> str:
    """Returns HTML for a colored score badge."""
    if score is None:
        return '<span class="badge-score-low">Unscored</span>'
    if score >= 80:
        return f'<span class="badge-score-high">★ {score}/100 High</span>'
    elif score >= 50:
        return f'<span class="badge-score-mid">● {score}/100 Medium</span>'
    else:
        return f'<span class="badge-score-low">○ {score}/100 Low</span>'


def seed_demo_leads(db) -> int:
    """Populates the database with realistic sample leads for immediate evaluation."""
    repo = LeadRepository(db)
    
    demo_leads = [
        {
            "business_name": "Austin Premier Dental & Orthodontics",
            "business_category": "Dental Clinic",
            "industry": "dental_clinic",
            "country": "USA",
            "state": "TX",
            "city": "Austin",
            "postal_code": "78701",
            "address": "410 Congress Ave, Suite 200, Austin, TX",
            "phone": "+1 (512) 555-0142",
            "email": "info@austinpremierdental.com",
            "website": "https://www.austinpremierdental.com",
            "google_place_id": "ChIJ_austin_dental_01",
            "google_maps_url": "https://maps.google.com/?q=Austin+Premier+Dental",
            "rating": 4.8,
            "review_count": 184,
            "hours": "Mon-Fri: 8AM - 5PM",
            "website_status": "200",
            "website_title": "Austin Premier Dental | General & Cosmetic Dentistry",
            "website_description": "Comprehensive dental care, invisalign, and emergency dentistry in downtown Austin.",
            "technology_stack": [
                {"technology_name": "WordPress", "category": "CMS"},
                {"technology_name": "Google Analytics", "category": "Analytics"},
            ],
            "ssl_enabled": True,
            "chatbot_detected": False,
            "whatsapp_detected": False,
            "booking_system": "None (Phone Only)",
            "primary_opportunity": "AI Receptionist & 24/7 Appointment Automation",
            "secondary_opportunities": ["WhatsApp Booking Assistant", "Local SEO Optimization"],
            "opportunity_reason": "High review volume (184 reviews, 4.8 rating) with no online booking system or after-hours chat capture.",
            "lead_score": 88,
            "score_breakdown": {
                "website_opportunity": 14,
                "technology_opportunity": 12,
                "service_fit": 18,
                "business_activity": 9,
                "review_strength": 9,
                "contactability": 10,
                "digital_weakness": 8,
                "commercial_potential": 8
            },
            "outreach_confidence": 0.88,
            "campaign": "dental",
            "pipeline_status": "ANALYZED",
            "generated_subject": "Quick question regarding appointment bookings for Austin Premier Dental",
            "generated_email": "Hi Dr. Austin Team,\n\nI came across Austin Premier Dental on Congress Ave—impressive 4.8 rating across 184 reviews!\n\nI noticed patients calling after hours or visiting your website can't book appointments instantly without waiting for office hours. At 100Solutionz, we deploy an AI dental receptionist that schedules patient visits 24/7 directly into your calendar and answers common questions via chat and WhatsApp.\n\nWould you be open to a brief 10-minute demo next Tuesday on how this recaptures missed after-hours patient inquiries?\n\nBest regards,\n100Solutionz Growth Team",
            "approved": False,
            "contact_status": "new",
            "email_status": "pending"
        },
        {
            "business_name": "Luxe Glow Med Spa & Aesthetics",
            "business_category": "Med Spa",
            "industry": "med_spa",
            "country": "USA",
            "state": "CA",
            "city": "Beverly Hills",
            "postal_code": "90210",
            "address": "9400 Wilshire Blvd, Beverly Hills, CA",
            "phone": "+1 (310) 555-8921",
            "email": "concierge@luxeglowmedspa.com",
            "website": "https://www.luxeglowmedspa.com",
            "google_place_id": "ChIJ_luxe_glow_bh_02",
            "google_maps_url": "https://maps.google.com/?q=Luxe+Glow+Med+Spa",
            "rating": 4.9,
            "review_count": 210,
            "hours": "Tue-Sat: 10AM - 7PM",
            "website_status": "200",
            "website_title": "Luxe Glow Medical Spa | Botox, Fillers & Laser Skin Care",
            "website_description": "Premier luxury medical spa offering non-surgical aesthetic enhancements and advanced skin rejuvenation.",
            "technology_stack": [
                {"technology_name": "Wix", "category": "CMS"},
                {"technology_name": "Meta Pixel", "category": "Advertising"}
            ],
            "ssl_enabled": True,
            "chatbot_detected": False,
            "whatsapp_detected": False,
            "primary_opportunity": "Custom Website Redesign & VIP Booking Automation",
            "secondary_opportunities": ["WhatsApp Concierge Automation", "High-Converting Retargeting Funnel"],
            "opportunity_reason": "High-end Beverly Hills clientele but running on a basic template with slow load times and no interactive consultation flow.",
            "lead_score": 92,
            "score_breakdown": {
                "website_opportunity": 15,
                "technology_opportunity": 14,
                "service_fit": 18,
                "business_activity": 10,
                "review_strength": 9,
                "contactability": 10,
                "digital_weakness": 8,
                "commercial_potential": 8
            },
            "outreach_confidence": 0.92,
            "campaign": "med_spa",
            "pipeline_status": "ANALYZED",
            "generated_subject": "Elevating the digital consultation flow for Luxe Glow",
            "generated_email": "Hi Luxe Glow Team,\n\nYour 4.9-star reputation in Beverly Hills is exceptional. While reviewing your site, I noticed the consultation booking flow relies on basic forms rather than an interactive VIP aesthetic intake.\n\nAt 100Solutionz, we build high-converting luxury web platforms paired with WhatsApp concierge automation that qualify aesthetic clients and secure deposits seamlessly.\n\nWould you have 10 minutes this Thursday to preview how our client intake flow increases booked high-ticket treatments?\n\nWarm regards,\n100Solutionz Team",
            "approved": True,
            "contact_status": "ready",
            "email_status": "pending"
        },
        {
            "business_name": "Apex Ridge Commercial Realty",
            "business_category": "Real Estate Agency",
            "industry": "real_estate",
            "country": "USA",
            "state": "FL",
            "city": "Miami",
            "postal_code": "33131",
            "address": "1111 Brickell Ave, Miami, FL",
            "phone": "+1 (305) 555-4309",
            "email": "leads@apexridgerealty.com",
            "website": "https://www.apexridgerealty.com",
            "google_place_id": "ChIJ_apex_ridge_fl_03",
            "google_maps_url": "https://maps.google.com/?q=Apex+Ridge+Commercial+Realty",
            "rating": 4.6,
            "review_count": 68,
            "hours": "Mon-Fri: 9AM - 6PM",
            "website_status": "200",
            "website_title": "Apex Ridge Realty | Commercial Real Estate & Investments",
            "website_description": "Industrial, office, and multifamily investments across South Florida.",
            "technology_stack": [
                {"technology_name": "Squarespace", "category": "CMS"},
                {"technology_name": "Google Analytics", "category": "Analytics"}
            ],
            "ssl_enabled": True,
            "chatbot_detected": False,
            "whatsapp_detected": False,
            "primary_opportunity": "AI Property Inquiry Chatbot & Lead Routing CRM",
            "secondary_opportunities": ["Commercial Listing Portal", "Targeted Investor Ads"],
            "opportunity_reason": "High-ticket commercial transactions requiring rapid response times to property inquiries, currently lacking automated lead qualification.",
            "lead_score": 85,
            "score_breakdown": {
                "website_opportunity": 13,
                "technology_opportunity": 11,
                "service_fit": 18,
                "business_activity": 8,
                "review_strength": 9,
                "contactability": 10,
                "digital_weakness": 8,
                "commercial_potential": 8
            },
            "outreach_confidence": 0.85,
            "campaign": "real_estate",
            "pipeline_status": "APPROVED",
            "generated_subject": "Automating commercial lead inquiries for Apex Ridge Realty",
            "generated_email": "Hi Apex Ridge Team,\n\nGiven the rapid movement in Brickell commercial real estate, quick response times to investor inquiries are crucial.\n\nWe build conversational AI agents for commercial brokers that qualify investor criteria (budget, square footage, cap rate targets) 24/7 and route qualified leads instantly to your deal team.\n\nCould we arrange a 10-minute briefing next week to show you how this accelerates deal velocity?\n\nBest regards,\n100Solutionz",
            "approved": True,
            "contact_status": "ready",
            "email_status": "pending"
        },
        {
            "business_name": "Artisan Roast Coffee Co.",
            "business_category": "E-commerce & Roastery",
            "industry": "ecommerce",
            "country": "USA",
            "state": "WA",
            "city": "Seattle",
            "postal_code": "98101",
            "address": "1520 Pike Pl, Seattle, WA",
            "phone": "+1 (206) 555-7712",
            "email": "orders@artisanroastseattle.com",
            "website": "https://www.artisanroastseattle.com",
            "google_place_id": "ChIJ_artisan_roast_wa_04",
            "google_maps_url": "https://maps.google.com/?q=Artisan+Roast+Coffee",
            "rating": 4.7,
            "review_count": 340,
            "hours": "Daily: 7AM - 6PM",
            "website_status": "200",
            "website_title": "Artisan Roast | Single Origin Specialty Coffee Subscriptions",
            "website_description": "Ethically sourced small batch coffee delivered to your doorstep.",
            "technology_stack": [
                {"technology_name": "Shopify", "category": "E-commerce"},
                {"technology_name": "Google Tag Manager", "category": "Analytics"}
            ],
            "ssl_enabled": True,
            "ecommerce_detected": True,
            "ecommerce_platform": "Shopify",
            "chatbot_detected": False,
            "primary_opportunity": "Shopify Conversion Rate Optimization & AI Shopping Concierge",
            "secondary_opportunities": ["Subscription Retention Automation", "Abandoned Cart WhatsApp Recovery"],
            "opportunity_reason": "Active Shopify store with strong social proof (340 reviews) that could lift repeat purchase rates with automated subscription personalization.",
            "lead_score": 89,
            "score_breakdown": {
                "website_opportunity": 14,
                "technology_opportunity": 14,
                "service_fit": 18,
                "business_activity": 10,
                "review_strength": 9,
                "contactability": 8,
                "digital_weakness": 8,
                "commercial_potential": 8
            },
            "outreach_confidence": 0.89,
            "campaign": "ecommerce",
            "pipeline_status": "ANALYZED",
            "generated_subject": "Idea for boosting subscription conversion on Artisan Roast",
            "generated_email": "Hi Artisan Roast Team,\n\nBig fan of your specialty single-origin roast program—340+ positive reviews is a huge achievement.\n\nWe help high-growth Shopify coffee brands implement personalized AI flavor matchers and abandoned cart recovery that consistently lift recurring subscription revenue by 15-25%.\n\nWould you be open to a short 10-minute idea exchange this week?\n\nCheers,\n100Solutionz",
            "approved": False,
            "contact_status": "new",
            "email_status": "pending"
        },
        {
            "business_name": "Vanguard Fitness & Performance",
            "business_category": "Gym & Fitness",
            "industry": "gym_fitness",
            "country": "USA",
            "state": "IL",
            "city": "Chicago",
            "postal_code": "60607",
            "address": "850 W Jackson Blvd, Chicago, IL",
            "phone": "+1 (312) 555-9011",
            "email": "membership@vanguardfitnesschi.com",
            "website": "https://www.vanguardfitnesschi.com",
            "google_place_id": "ChIJ_vanguard_chi_05",
            "google_maps_url": "https://maps.google.com/?q=Vanguard+Fitness+Chicago",
            "rating": 4.5,
            "review_count": 92,
            "hours": "Mon-Sun: 5AM - 11PM",
            "website_status": "200",
            "technology_stack": [
                {"technology_name": "WordPress", "category": "CMS"}
            ],
            "ssl_enabled": True,
            "chatbot_detected": False,
            "primary_opportunity": "Lead Capture WhatsApp Automation & Free Pass Funnel",
            "secondary_opportunities": ["Mobile App Integration", "Local Gym SEO"],
            "opportunity_reason": "High foot-traffic location with basic website lacking automated free day-pass download or SMS lead nurturing.",
            "lead_score": 79,
            "score_breakdown": {
                "website_opportunity": 12,
                "technology_opportunity": 10,
                "service_fit": 16,
                "business_activity": 8,
                "review_strength": 8,
                "contactability": 9,
                "digital_weakness": 8,
                "commercial_potential": 8
            },
            "outreach_confidence": 0.79,
            "campaign": "gym_fitness",
            "pipeline_status": "DISCOVERED",
            "generated_subject": "Boosting trial member signups for Vanguard Fitness",
            "generated_email": "Hi Vanguard Fitness Team,\n\nI noticed Vanguard Fitness has built a strong community in West Loop with 90+ stellar reviews.\n\nMany gyms lose 60% of website visitors because requesting a trial pass requires waiting for a manual email reply. We set up instant WhatsApp/SMS trial pass delivery that books prospective members into intro workouts within minutes.\n\nOpen to seeing a 2-minute demo of how this works?\n\nBest,\n100Solutionz",
            "approved": False,
            "contact_status": "new",
            "email_status": "pending"
        }
    ]

    added = 0
    for data in demo_leads:
        _, is_new = repo.create_or_update(data)
        if is_new:
            added += 1
    return added
