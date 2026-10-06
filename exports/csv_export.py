from pathlib import Path
from typing import List, Dict, Any
import pandas as pd


class CSVExporter:
    def export(self, leads: List[Dict[str, Any]], output_path: str = "data/leads.csv"):
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df = pd.DataFrame(leads)
        df.to_csv(output_path, index=False)
        return str(output_path)
