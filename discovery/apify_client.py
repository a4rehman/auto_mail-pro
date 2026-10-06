import os
from typing import Dict, Any, List
from tenacity import retry, stop_after_attempt, wait_exponential
from core.exceptions import DiscoveryError


class ApifyClient:
    def __init__(self, api_token: str = None, actor_id: str = None):
        self.api_token = api_token or os.getenv("APIFY_API_TOKEN", "")
        self.actor_id = actor_id or os.getenv("APIFY_ACTOR_ID", "")
        self._client = None
    
    def _get_client(self):
        if self._client is None:
            try:
                from apify_client import ApifyClient as Client
                self._client = Client(self.api_token)
            except ImportError:
                raise DiscoveryError("apify-client not installed")
        return self._client
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def run_actor(self, input_data: Dict[str, Any], actor_id: str = None) -> Dict[str, Any]:
        actor_id = actor_id or self.actor_id
        if not actor_id:
            raise DiscoveryError("APIFY_ACTOR_ID not configured")
        try:
            client = self._get_client()
            run = client.actor(actor_id).call(run_input=input_data)
            return run
        except Exception as e:
            raise DiscoveryError(f"Apify run failed: {str(e)}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_dataset_items(self, dataset_id: str) -> List[Dict[str, Any]]:
        try:
            client = self._get_client()
            items = client.dataset(dataset_id).list_items().items
            return items
        except Exception as e:
            raise DiscoveryError(f"Failed to fetch dataset items: {str(e)}")
    
    def run_and_get_items(self, input_data: Dict[str, Any], actor_id: str = None) -> List[Dict[str, Any]]:
        run = self.run_actor(input_data, actor_id)
        dataset_id = run.get("defaultDatasetId") or run.get("datasetId")
        if not dataset_id:
            return []
        return self.get_dataset_items(dataset_id)
