import os
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from supabase import create_client

def scrape_historical_leads():
    print("--- 📂 RECHERCHE DES PROJETS (NOV 2025 - FÉB 2026) ---")
    
    url_supabase = os.environ.get("SUPABASE_URL")
    key_supabase = os.environ.get("SUPABASE_KEY")
    supabase = create_client(url_supabase, key_supabase)

    leads_extraits = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    # Requêtes ciblées sur les 3 derniers mois pour le 73, 74, 01
    cibles = [
        {"q": "permis+construire+commercial+2025+2026+haute-savoie", "type": "Permis Récent"},
        {"q": "nouveau+lotissement+haute-savoie+2025", "type": "Résidentiel Neuf"},
        {"q": "chantier+entrepôt+logistique+savoie+73", "type": "Industrie / Logistique"},
        {"q": "ouverture+magasin+prévue+2026+annecy+chambéry", "type": "Commerce Futur"},
        {"q": "travaux+parking+aménagement+ain+01", "type": "Parking / Voirie"}
    ]

    for cible in cibles:
        print(f"🔎 Exploration historique : {cible['type']}...")
        # L'ajout de dates dans la requête force Google à sortir les archives récentes
        google_url = f"https://news.google.com/search?q={cible['q']}&hl=fr&gl=FR&ceid=FR:fr"
        
        try:
            page = requests.get(google_url, headers=headers, timeout=15)
            soup = BeautifulSoup(page.text, 'html.parser')
            articles = soup.find_all('article', limit=8) # On prend plus de résultats

            for art in articles:
                titre_elem = art.find('a', class_='J7YVsc') or art.find('h3')
                if titre_elem:
                    titre = titre_elem.text
                    link_elem = art.find('a')
                    lien = "https://news.google.com" + link_elem['href'][1:] if link_elem else "Lien indisponible"
                    
                    # Logique de tri par département
                    dept = "74"
                    if "73" in titre or "Savoie" in titre: dept = "73"
                    if "01" in titre or "Ain" in titre: dept = "01"

                    leads_extraits.append({
                        "name": titre[:120],
                        "type": cible['type'],
                        "location": f"Secteur {dept}",
                        "notes": "Détecté dans les archives 3 mois. Potentiel chantier en cours.",
                        "estimated_value": "À chiffrer",
                        "status": "new",
                        "source_url": lien,
                        "department": dept,
                        "created_at": datetime.now().isoformat()
                    })
        except Exception as e:
            print(f"Erreur : {e}")

    # Envoi massif vers Supabase
    if leads_extraits:
        try:
            # On utilise insert pour remplir le tableau
            supabase.table("leads").insert(leads_extraits).execute()
            print(f"✅ MISSION RÉUSSIE : {len(leads_extraits)} projets trouvés sur 3 mois !")
        except Exception as e:
            print(f"Erreur Supabase : {e}")
    else:
        print("⚠️ Toujours rien dans les archives. On va élargir encore les mots-clés.")

if __name__ == "__main__":
    scrape_historical_leads()
