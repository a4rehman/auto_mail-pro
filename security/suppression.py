from datetime import datetime
from typing import Dict, Any, Optional


class SuppressionList:
    def __init__(self):
        self._data = []
    
    def add(self, email: str, reason: str = "manual"):
        if not email:
            return
        self._data.append({
            "email": email.lower(),
            "reason": reason,
            "suppressed_at": datetime.utcnow()
        })
    
    def is_suppressed(self, email: str) -> bool:
        if not email:
            return False
        el = email.lower()
        return any(s['email'] == el for s in self._data)
