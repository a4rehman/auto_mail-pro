from typing import Dict, Any


class FollowUpManager:
    def get_sequence(self) -> list:
        return [
            {"day": 3, "template": "followup_1"},
            {"day": 7, "template": "followup_2"},
            {"day": 14, "template": "followup_3"},
        ]
