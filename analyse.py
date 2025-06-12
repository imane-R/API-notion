import pandas as pd

def extract_data_from_notion(interventions):
    data = []

    for item in interventions:
        props = item["properties"]
        data.append({
            "Cours": props["Cours"]["title"][0]["text"]["content"] if props["Cours"]["title"] else None,
            "École": props["Ecole"]["select"]["name"] if props["Ecole"]["select"] else None,
            "Classe": props["Classe"]["select"]["name"] if props["Classe"]["select"] else None,
            "Heures": props["Nombre heures"]["number"],
            "Tarif horaire": props["Tarif horaire"]["number"],
            "Total": round(props["Nombre heures"]["number"] * props["Tarif horaire"]["number"], 2)
        })

    df = pd.DataFrame(data)
    return df
