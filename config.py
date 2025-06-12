from dotenv import load_dotenv
import os

load_dotenv()  # Charge les variables du fichier .env

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DB_INTERVENTIONS_ID = os.getenv("DB_INTERVENTIONS_ID")
DB_INVOICES_ID = os.getenv("DB_INVOICES_ID")

print("Clés chargées avec succès.")
