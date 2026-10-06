# DEPLOYMENT.md

## Local
pip install -r requirements.txt
cp .env.example .env
streamlit run app/streamlit_app.py

## Streamlit Cloud
- Push repo to GitHub
- Connect to share.streamlit.io
- Configure secrets in Advanced Settings (.env vars as secrets.toml)
- Note: Playwright heavy jobs may need separate worker if used; Apify runs server-side

## Production Considerations
- Use PostgreSQL/Supabase
- Set DRY_RUN=false only after approval/testing
- Configure proper SMTP + suppression
- Set ENVIRONMENT=production, DEBUG=false
