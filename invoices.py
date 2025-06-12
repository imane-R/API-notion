import requests
from config import DB_INVOICES_ID
from notion_utils import HEADERS


def create_invoice_page(client: str, interventions: list, total: float, mois: str, invoice_number: str):
    children = generate_invoice_blocks(interventions, total, client, mois)

    payload = {
        "parent": {"database_id": DB_INVOICES_ID},
        "properties": {
            "Client": {
                "title": [{"text": {"content": client}}]
            },
            "Mois": {
                "rich_text": [{"text": {"content": mois}}]
            },
            "Total Amount": {
                "number": total
            },
            "Invoice Number": {
                "rich_text": [{"text": {"content": invoice_number}}]
            }
        },
        "children": children
    }

    response = requests.post("https://api.notion.com/v1/pages", headers=HEADERS, json=payload)
    response.raise_for_status()
    print(f"✅ Facture {invoice_number} créée pour {client}")
    return response.json()

def generate_invoice_blocks(interventions, total, client, mois):
    children = [
        {
            "object": "block",
            "type": "heading_1",
            "heading_1": {"rich_text": [{"type": "text", "text": {"content": "FACTURE"}}]}
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": f"Client : {client}"}}]}
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": f"Mois : {mois}"}}]}
        },
        {"object": "block", "type": "divider", "divider": {}},
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": "Détail des interventions"}}]}
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{
                    "type": "text",
                    "text": {"content": "Cours | Heures | Tarif | Total"}
                }]
            }
        }
    ]

    # Détail des prestations
    for item in interventions:
        props = item["properties"]
        cours = props["Cours"]["title"][0]["text"]["content"] if props["Cours"]["title"] else ""
        heures = props["Nombre heures"]["number"]
        tarif = props["Tarif horaire"]["number"]
        total_ligne = round(heures * tarif, 2)
        ligne = f"{cours} | {heures}h | {tarif}€ | {total_ligne}€"

        children.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": ligne}}]
            }
        })

    # Bloc total
    children.append({
        "object": "block",
        "type": "callout",
        "callout": {
            "icon": {"type": "emoji", "emoji": "💰"},
            "rich_text": [{"type": "text", "text": {"content": f"Total à payer : {total} €"}}]
        }
    })

    return children

def mark_as_billed(pages):
    for page in pages:
        page_id = page["id"]

        update_payload = {
            "properties": {
                "Facturé": {
                    "checkbox": True
                }
            }
        }

        response = requests.patch(
            f"https://api.notion.com/v1/pages/{page_id}",
            headers=HEADERS,
            json=update_payload
        )
        response.raise_for_status()
        print(f"✅ Page {page_id} marquée comme facturée")


