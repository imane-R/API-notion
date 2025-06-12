from config import NOTION_TOKEN, DB_INTERVENTIONS_ID
import requests
from datetime import datetime

# Les entêtes API Notion
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}
print("Headers définis :", HEADERS)

# Fonction pour interroger les interventions non facturées entre 2 dates
def query_unbilled_entries(date_begin: str, date_end: str, a_ete_facture: bool = False):
    query = {
        "filter": {
            "and": [
                {
                    "property": "Facturé",
                    "checkbox": {"equals": a_ete_facture}
                },
                {
                    "property": "Date de début",
                    "date": {"on_or_after": date_begin}
                },
                {
                    "property": "Date de début",
                    "date": {"before": date_end}
                }
            ]
        }
    }

    url = f"https://api.notion.com/v1/databases/{DB_INTERVENTIONS_ID}/query"
    response = requests.post(url, headers=HEADERS, json=query)
    response.raise_for_status()
    return response.json()["results"]

