import os
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from supabase import create_client

def scrape_expert_system():
    print("--- 🚀 DÉMARRAGE DU MOTEUR EXPERT PROGMARQUAGE (73, 74, 01) ---")
    
    url_supabase = os.environ.get("SUPABASE_URL")
    key_supabase = os.environ.get("SUPABASE_KEY")
    supabase = create_client(url_supabase, key_supabase)

    leads_extraits = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    # STRATÉGIE MULTI-SOURCES : On cible l'intention de construire
    cibles = [
        {"q": "avis+depot+permis+de+construire+commercial+74", "type": "Permis de Construire"},
        {"q": "consultation+publique+projet+immobilier+annecy", "type": "Résidence / Collectif"},
        {"q": "nouvelle+zone+artisanale+savoie+73", "type": "Industrie / Zone Pro"},
        {"q": "extension+plateforme+logistique+ain+01", "type": "Logistique / Marquage Intérieur"},
        {"q": "ouverture+prochaine+magasin+haute-savoie", "type": "Commerce"},
        {"q": "boulangerie+en+construction+savoie", "type": "Boulangerie"}
    ]

    for cible in cibles:
        print(f"🔎 Analyse : {cible['type']}...")
        google_url = f"https://news.google.com/search?q={cible['q']}&hl=fr&gl=FR&ceid=FR:fr"
        
        try:
            page = requests.get(google_url, headers=headers, timeout=15)
            soup = BeautifulSoup(page.text, 'html.parser')
            articles = soup.find_all('article', limit=4)

            for art in articles:
                titre_elem = art.find('a', class_='J7YVsc') or art.find('h3')
                if titre_elem:
                    titre = titre_elem.text
                    # Récupération du lien
                    link_elem = art.find('a')
                    lien = "https://news.google.com" + link_elem['href'][1:] if link_elem else "Lien indisponible"
                    
                    # Détection du département
                    dept = "74"
                    if "73" in titre or "Savoie" in titre: dept = "73"
                    if "01" in titre or "Ain" in titre: dept = "01"

                    lead = {
                        "name": titre[:120],
                        "type": cible['type'],
                        "location": f"Détecté en {dept}",
                        "notes": f"INDICE FORT : {cible['type']} détecté via presse/annonces.",
                        "estimated_value": "À chiffrer",
                        "status": "new",
                        "source_url": lien,
                        "department": dept,
                        "created_at": datetime.now().isoformat()
                    }
                    leads_extraits.append(lead)
        except Exception as e:
            print(f"Erreur sur {cible['type']}: {e}")

    # SAUVEGARDE DU FICHIER ARTEFACT
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"leads_progmarquage_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(leads_extraits, f, ensure_ascii=False, indent=2)

    # ENVOI VERS SUPABASE
    if leads_extraits:
        try:
            supabase.table("leads").insert(leads_extraits).execute()
            print(f"✅ TERMINÉ : {len(leads_extraits)} projets envoyés au SaaS.")
        except Exception as e:
            print(f"Erreur Supabase : {e}")
    else:
        print("⚠️ Aucune nouvelle annonce détectée aujourd'hui.")

if __name__ == "__main__":
    scrape_expert_system()
