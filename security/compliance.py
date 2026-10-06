from config.settings import settings


class ComplianceManager:
    def get_sender_identity(self) -> dict:
        return {
            "business_name": settings.BUSINESS_NAME,
            "business_address": settings.BUSINESS_ADDRESS,
            "sender_name": settings.SENDER_NAME,
            "sender_email": settings.SENDER_EMAIL,
            "unsubscribe_enabled": settings.UNSUBSCRIBE_ENABLED
        }
