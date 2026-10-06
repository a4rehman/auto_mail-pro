class LeadPlatformError(Exception):
    """Base exception for Lead Platform."""
    pass


class DiscoveryError(LeadPlatformError):
    """Error in lead discovery."""
    pass


class EnrichmentError(LeadPlatformError):
    """Error in lead enrichment."""
    pass


class AIError(LeadPlatformError):
    """Error in AI processing."""
    pass


class ValidationError(LeadPlatformError):
    """Validation error."""
    pass


class DatabaseError(LeadPlatformError):
    """Database operation error."""
    pass


class SendError(LeadPlatformError):
    """Email sending error."""
    pass
