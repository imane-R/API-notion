from notion_utils import query_unbilled_entries
from analyse import extract_data_from_notion
from invoices import create_invoice_page, mark_as_billed

# Extrait du mois de juin 2025
interventions = query_unbilled_entries("2025-04-24", "2025-06-30")

for i, item in enumerate(interventions):
    print(f"{i+1}. {item['properties']['Cours']['title'][0]['text']['content']}")

df = extract_data_from_notion(interventions)

#  Affichage des données
print("\n--- Aperçu des interventions ---")
print(df)

#  Total par école
print("\n--- Heures & total par école ---")
print(df.groupby("École")[["Heures", "Total"]].sum())

#  Heures par école et par classe
print("\n--- Heures par école et classe ---")
print(df.groupby(["École", "Classe"])["Heures"].sum())

print(df.groupby("École")[["Heures", "Total"]].sum().sort_values("Total", ascending=False))
df.to_csv("interventions.csv", index=False)

# Creation du facture

# Étape 1 — Récupérer les interventions de juin
interventions = query_unbilled_entries("2025-03-01", "2025-06-30")

# Étape 2 — Filtrer par client
client = "ECE"
interventions_client = [
    i for i in interventions
    if i["properties"]["Ecole"]["select"]
    and i["properties"]["Ecole"]["select"]["name"] == client
]

# Étape 3 — Calculer le total à facturer
total = sum([
    i["properties"]["Nombre heures"]["number"] * i["properties"]["Tarif horaire"]["number"]
    for i in interventions_client
])

# Étape 4 — Créer la facture
create_invoice_page(client, interventions_client, total, "2025-07", "Imane-Benamar")

mark_as_billed(interventions_client)



