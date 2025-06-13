
import streamlit as st
from dotenv import load_dotenv
import os
import requests
from datetime import datetime
import pandas as pd

from invoices import create_invoice_page, mark_as_billed

# 🔐 Chargement des clés
load_dotenv()
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DB_INTERVENTIONS_ID = os.getenv("DB_INTERVENTIONS_ID")

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

# 📥 Requête Notion pour extraire les interventions
def query_unbilled_entries(date_begin: str, date_end: str):
    query = {
        "filter": {
            "and": [
                {"property": "Facturé", "checkbox": {"equals": False}},
                {"property": "Date de début", "date": {"on_or_after": date_begin}},
                {"property": "Date de début", "date": {"before": date_end}}
            ]
        }
    }
    url = f"https://api.notion.com/v1/databases/{DB_INTERVENTIONS_ID}/query"
    res = requests.post(url, headers=HEADERS, json=query)
    res.raise_for_status()
    return res.json()["results"]

def extract_df(interventions):
    rows = []
    for i in interventions:
        p = i["properties"]
        rows.append({
            "Cours": p["Cours"]["title"][0]["text"]["content"] if p["Cours"]["title"] else None,
            "École": p["Ecole"]["select"]["name"] if p["Ecole"]["select"] else None,
            "Classe": p["Classe"]["select"]["name"] if p["Classe"]["select"] else None,
            "Heures": p["Nombre heures"]["number"],
            "Tarif horaire": p["Tarif horaire"]["number"],
            "Total": round(p["Nombre heures"]["number"] * p["Tarif horaire"]["number"], 2),
            "id": i["id"]
        })
    return pd.DataFrame(rows)

# --- INTERFACE STREAMLIT ---
st.title("🧾 Facturation Notion")
st.markdown("Automatiser la création et la validation des factures pour les profs freelance.")

# Dates
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("📅 Date de début", datetime(2025, 6, 1))
with col2:
    end_date = st.date_input("📅 Date de fin", datetime(2025, 6, 30))

# Bouton pour charger les données
if st.button("🔍 Charger les interventions"):
    raw_data = query_unbilled_entries(str(start_date), str(end_date))
    df = extract_df(raw_data)
    st.session_state["df"] = df
    st.session_state["raw_data"] = raw_data
    st.success(f"{len(df)} interventions chargées.")
    st.dataframe(df)

# Si interventions chargées
if "df" in st.session_state:
    df = st.session_state["df"]
    raw_data = st.session_state["raw_data"]
    clients = df["École"].dropna().unique()
    client = st.selectbox("👨‍🏫 Choisir un client", clients)

    df_client = df[df["École"] == client]
    interventions_client = [
        i for i in raw_data
        if i["properties"]["Ecole"]["select"]
        and i["properties"]["Ecole"]["select"]["name"] == client
    ]

    total = df_client["Total"].sum()
    mois = f"{start_date.year}-{start_date.month:02d}"
    invoice_number = st.text_input("🧾 Numéro de facture", f"E{datetime.now().strftime('%H%M')}")

    if st.button("✅ Créer la facture"):
        create_invoice_page(client, interventions_client, total, mois, invoice_number)
        st.success(f"✅ Facture {invoice_number} créée dans Notion pour {client}")

    if st.button("📌 Marquer comme facturé"):
        mark_as_billed(interventions_client)
        st.success("✅ Interventions marquées comme facturées.")
