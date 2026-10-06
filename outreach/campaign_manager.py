from typing import List, Dict, Any
import yaml
from pathlib import Path


class CampaignManager:
    def __init__(self, config_path: str = "config/campaigns.yaml"):
        self.config_path = Path(config_path)
        self._load()
    
    def _load(self):
        if self.config_path.exists():
            with open(self.config_path) as f:
                self.campaigns = yaml.safe_load(f) or {}
        else:
            self.campaigns = {}
    
    def get_campaign_services(self, industry: str) -> List[str]:
        for key, cfg in self.campaigns.items():
            if key in str(industry).lower() or str(industry).lower() in key:
                return cfg.get('services', [])
        return ["Website Development", "Local SEO", "Business Automation"]
