import requests
from config import DB_INTERVENTIONS_ID
from notion_utils import HEADERS

def get_database_properties(database_id):
    url = f"https://api.notion.com/v1/databases/{database_id}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()["properties"]

props = get_database_properties(DB_INTERVENTIONS_ID)
for name, data in props.items():
    print(f"{name} ➜ {data['type']}")
