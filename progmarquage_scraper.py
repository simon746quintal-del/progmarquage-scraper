import os
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from supabase import create_client

def scrape_deep_leads():
    print("--- RECHERCHE DE CHANTIERS RÉELS (73, 74, 01) ---")
    
    url_supabase = os.environ.get("SUPABASE_URL")
    key_supabase = os.environ.get("SUPABASE_KEY")
    supabase = create_client(url_supabase, key_supabase)

    leads_reels = []
    # On cherche des mots-clés très précis de "chantier" ou "permis"
    requetes = [
        "permis+de+construire+commerce+haute-savoie",
        "construction+entrepot+savoie",
        "nouvelle+zone+commerciale+ain"
    ]

    for req in requetes:
        # On interroge Google News pour avoir les articles de presse récents
        google_url = f"https://news.google.com/search?q={req}&hl=fr&gl=FR&ceid=FR:fr"
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            page = requests.get(google_url, headers=headers)
            soup = BeautifulSoup(page.text, 'html.parser')
            
            # On prend les 3 premiers articles de chaque recherche
            articles = soup.find_all('article', limit=3)
            for art in articles:
                titre = art.find('a', class_='J7YVsc')
                if titre:
                    titre_texte = titre.text
                    lien = "https://news.google.com" + titre['href'][1:]
                    
                    lead = {
                        "name": titre_texte[:100],
                        "type": "Chantier Détecté",
                        "location": "73/74/01",
                        "notes": "Vérifier l'adresse exacte dans l'article source.",
                        "estimated_value": "À chiffrer",
                        "status": "new",
                        "source_url": lien, # LE LIEN RÉEL POUR TES YEUX
                        "department": "74"
                    }
                    leads_reels.append(lead)
        except Exception as e:
            print(f"Erreur recherche : {e}")

    # On enregistre le fichier pour GitHub
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    with open(f"leads_progmarquage_{timestamp}.json", 'w', encoding='utf-8') as f:
        json.dump(leads_reels, f, ensure_ascii=False, indent=2)

    # Envoi Supabase
    if leads_reels:
        supabase.table("leads").insert(leads_reels).execute()
        print(f"✅ {len(leads_reels)} vrais projets envoyés !")

if __name__ == "__main__":
    scrape_deep_leads()
