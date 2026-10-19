import sys
from pathlib import Path
import asyncio
import streamlit as st

# Add project root to sys.path
ROOT_DIR = Path(__file__).parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.ui_utils import init_page, get_db, render_score_badge
from database.repository import LeadRepository
from database.models import Lead
from enrichment.website_analyzer import WebsiteAnalyzer
from intelligence.business_classifier import BusinessClassifier
from intelligence.opportunity_detector import OpportunityDetector
from intelligence.lead_scoring import LeadScorer

init_page("Website Intelligence & Technology Audit", "🔬")

tab_live, tab_batch = st.tabs(["🌐 Live URL Deep Audit", "⚡ Batch Enrich Database Leads"])

# ==========================================
# TAB 1: LIVE URL AUDIT
# ==========================================
with tab_live:
    st.markdown("### Real-Time Website Inspection")
    st.caption("Perform an instant live audit on any business website to uncover technology stack, tracking pixels, booking tools, and commercial opportunities.")

    target_url = st.text_input("Enter Target Website URL", placeholder="https://www.example.com", value="https://www.example.com")
    biz_name_hint = st.text_input("Business Name (Optional)", placeholder="e.g. Example Co.")

    if st.button("🚀 Run Live Audit", type="primary", use_container_width=True):
        if not target_url:
            st.error("Please enter a valid website URL.")
        else:
            with st.spinner("Crawling website, analyzing technology signatures, and scoring..."):
                try:
                    analyzer = WebsiteAnalyzer(timeout=15)
                    audit_res = asyncio.run(analyzer.analyze(target_url))

                    # Classify
                    classifier = BusinessClassifier()
                    class_res = classifier.classify({
                        "business_name": biz_name_hint or audit_res.get("website_title"),
                        "website": target_url,
                        "website_description": audit_res.get("website_description")
                    })

                    # Opportunity detection
                    opp_detector = OpportunityDetector()
                    opp_res = opp_detector.detect({
                        "business_name": biz_name_hint or audit_res.get("website_title"),
                        "industry": class_res.get("industry"),
                        "website": target_url,
                        "technology_stack": audit_res.get("technology_stack", [])
                    })

                    # Scoring
                    lead_scorer = LeadScorer()
                    score_res = lead_scorer.score({
                        "website": target_url,
                        "technology_stack": audit_res.get("technology_stack", []),
                        "primary_opportunity": opp_res.get("primary_opportunity"),
                        "rating": 4.5,
                        "review_count": 25,
                        "email": audit_res.get("emails_found")[0] if audit_res.get("emails_found") else None
                    })

                    st.session_state["live_audit_result"] = {
                        "url": target_url,
                        "name": biz_name_hint or audit_res.get("website_title") or "Prospective Business",
                        "audit": audit_res,
                        "classification": class_res,
                        "opportunity": opp_res,
                        "score": score_res
                    }
                    st.success("Audit complete!")
                except Exception as e:
                    st.error(f"Live audit failed: {e}")

    if "live_audit_result" in st.session_state and st.session_state["live_audit_result"]:
        res = st.session_state["live_audit_result"]
        audit = res["audit"]
        opp = res["opportunity"]
        sc = res["score"]
        cls_info = res["classification"]

        st.write("")
        st.markdown(f"### 📊 Audit Report: **{res['name']}**")
        
        # Overview Cards
        o1, o2, o3, o4 = st.columns(4)
        o1.metric("HTTP Status", audit.get("website_status", "N/A"))
        o2.metric("SSL Security", "✅ Active" if audit.get("ssl_enabled") else "❌ Missing")
        o3.metric("Chatbot / WhatsApp", "✅ Detected" if (audit.get("chatbot_detected") or audit.get("whatsapp_detected")) else "❌ None")
        o4.metric("Commercial Score", f"{sc.get('lead_score', 0)}/100")

        # Details
        d1, d2 = st.columns(2)
        with d1:
            st.markdown("#### 🛠️ Detected Technology Stack")
            tech_stack = audit.get("technology_stack", [])
            if tech_stack:
                for t in tech_stack:
                    st.markdown(f"- **{t.get('technology_name')}** `{t.get('category')}`")
            else:
                st.info("No standard framework or pixel detected (custom build or static HTML).")

            st.write("")
            st.markdown("#### 📧 Extracted Contact Data")
            emails = audit.get("emails_found", [])
            if emails:
                for em in emails:
                    st.markdown(f"- ✉️ `{em}`")
            else:
                st.caption("No direct emails found on homepage.")

            socials = audit.get("social_links", [])
            if socials:
                for soc in socials:
                    st.markdown(f"- 🔗 [{soc}]({soc})")

        with d2:
            st.markdown("#### 🎯 Identified 100Solutionz Opportunities")
            st.success(f"**Primary Service:** {opp.get('primary_opportunity')}")
            st.write(f"**Rationale:** {opp.get('opportunity_reason')}")
            
            secs = opp.get("secondary_opportunities", [])
            if secs:
                st.markdown("**Additional Services:**")
                for s in secs:
                    st.markdown(f"- {s}")

            st.write("")
            st.markdown("#### 📈 Score Component Breakdown")
            for cat, pts in sc.get("score_breakdown", {}).items():
                st.progress(min(pts / 20.0, 1.0), text=f"{cat.replace('_', ' ').title()}: {pts} pts")

        # Save to DB option
        st.write("")
        if st.button("💾 Save as Verified Lead in Database", type="primary", use_container_width=True):
            db = get_db()
            repo = LeadRepository(db)
            lead_dict = {
                "business_name": res["name"],
                "website": res["url"],
                "email": emails[0] if emails else None,
                "industry": cls_info.get("industry", "local_business"),
                "business_category": cls_info.get("industry", "Local Business").replace("_", " ").title(),
                "website_status": audit.get("website_status"),
                "website_title": audit.get("website_title"),
                "website_description": audit.get("website_description"),
                "technology_stack": audit.get("technology_stack"),
                "ssl_enabled": audit.get("ssl_enabled"),
                "chatbot_detected": audit.get("chatbot_detected"),
                "whatsapp_detected": audit.get("whatsapp_detected"),
                "ecommerce_detected": audit.get("ecommerce_detected"),
                "ecommerce_platform": audit.get("ecommerce_platform"),
                "primary_opportunity": opp.get("primary_opportunity"),
                "secondary_opportunities": opp.get("secondary_opportunities"),
                "opportunity_reason": opp.get("opportunity_reason"),
                "lead_score": sc.get("lead_score"),
                "score_breakdown": sc.get("score_breakdown"),
                "outreach_confidence": sc.get("outreach_confidence"),
                "pipeline_status": "ANALYZED"
            }
            lead_obj, is_new = repo.create_or_update(lead_dict)
            db.close()
            st.success(f"Successfully saved to database (Lead ID: {lead_obj.id})!")

# ==========================================
# TAB 2: BATCH ENRICHMENT
# ==========================================
with tab_batch:
    st.markdown("### Batch Intelligence Enrichment")
    st.caption("Scan all database prospects that lack website intelligence or opportunity scoring.")

    db = get_db()
    un_enriched = db.query(Lead).filter(
        (Lead.lead_score.is_(None)) | (Lead.pipeline_status == "DISCOVERED")
    ).all()
    db.close()

    st.write(f"Found **{len(un_enriched)}** leads requiring intelligence audit.")

    if un_enriched:
        if st.button("⚡ Run Full Pipeline for All Pending Leads", type="primary"):
            progress_bar = st.progress(0, text="Initializing enrichment...")
            db = get_db()
            repo = LeadRepository(db)
            analyzer = WebsiteAnalyzer(timeout=10)
            opp_detector = OpportunityDetector()
            scorer = LeadScorer()

            for idx, lead_item in enumerate(un_enriched):
                progress_bar.progress((idx + 1) / len(un_enriched), text=f"Analyzing {lead_item.business_name}...")
                
                # Fetch lead in current session
                l_rec = db.query(Lead).filter(Lead.id == lead_item.id).first()
                if l_rec.website:
                    try:
                        aud = asyncio.run(analyzer.analyze(l_rec.website))
                        l_rec.website_status = aud.get("website_status")
                        l_rec.website_title = aud.get("website_title")
                        l_rec.website_description = aud.get("website_description")
                        l_rec.ssl_enabled = aud.get("ssl_enabled")
                        l_rec.technology_stack = aud.get("technology_stack")
                        l_rec.chatbot_detected = aud.get("chatbot_detected")
                        l_rec.whatsapp_detected = aud.get("whatsapp_detected")
                        l_rec.ecommerce_detected = aud.get("ecommerce_detected")
                        l_rec.ecommerce_platform = aud.get("ecommerce_platform")
                        if not l_rec.email and aud.get("emails_found"):
                            l_rec.email = aud["emails_found"][0]
                    except Exception:
                        pass

                opp_res = opp_detector.detect({
                    "business_name": l_rec.business_name,
                    "industry": l_rec.industry or l_rec.business_category,
                    "website": l_rec.website,
                    "technology_stack": l_rec.technology_stack or []
                })
                l_rec.primary_opportunity = opp_res.get("primary_opportunity")
                l_rec.secondary_opportunities = opp_res.get("secondary_opportunities")
                l_rec.opportunity_reason = opp_res.get("opportunity_reason")

                sc_res = scorer.score({
                    "website": l_rec.website,
                    "technology_stack": l_rec.technology_stack or [],
                    "primary_opportunity": l_rec.primary_opportunity,
                    "rating": l_rec.rating or 4.5,
                    "review_count": l_rec.review_count or 20,
                    "email": l_rec.email,
                    "phone": l_rec.phone
                })
                l_rec.lead_score = sc_res["lead_score"]
                l_rec.score_breakdown = sc_res["score_breakdown"]
                l_rec.outreach_confidence = sc_res["outreach_confidence"]
                l_rec.pipeline_status = "ANALYZED"
                db.commit()

            db.close()
            st.success(f"Successfully processed and scored all {len(un_enriched)} leads!")
            st.rerun()
    else:
        st.success("All leads in your database are fully enriched and scored!")
