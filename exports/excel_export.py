from pathlib import Path
from typing import List, Dict, Any
import pandas as pd


class ExcelExporter:
    def export(self, leads: List[Dict[str, Any]], output_path: str = "data/leads_export.xlsx"):
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        df = pd.DataFrame(leads)
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Main leads sheet
            df.to_excel(writer, sheet_name='Leads', index=False)
            # Filtered sheets if columns exist
            if 'lead_score' in df.columns:
                high = df[df['lead_score'] >= 80]
                high.to_excel(writer, sheet_name='High Priority', index=False)
            if 'approved' in df.columns:
                approved = df[df['approved'] == True]
                approved.to_excel(writer, sheet_name='Approved', index=False)
            if 'email_status' in df.columns:
                sent = df[df['email_status'] == 'sent']
                sent.to_excel(writer, sheet_name='Sent', index=False)
        return str(output_path)
