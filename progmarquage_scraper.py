import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client

# Configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def scrape_real_leads():
    print("--- RECHERCHE AUTOMATIQUE DE CHANTIERS (73, 74, 01) ---")
    leads_trouves = []
    
    # On cible les mots-clés de construction et ouvertures
    queries = [
        "permis+de+construire+commerce+savoie",
        "construction+entrepot+haute-savoie",
        "ouverture+boulangerie+ain",
        "projet+zone+commerciale+74"
    ]

    for query in queries:
        # On utilise Google News pour trouver les annonces de chantiers récents
        url = f"https://news.google.com/search?q={query}&hl=fr&gl=FR&ceid=FR:fr"
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.find_all('article', limit=5)

            for art in articles:
                title = art.find('a', class_='J7YVsc')
                if title:
                    title_text = title.text
                    link = "https://news.google.com" + title['href'][1:]
                    
                    # On crée le lead pour ton SaaS
                    lead = {
                        "name": title_text[:100],
                        "type": "À déterminer",
                        "location": "Savoie / Ain", # Le script affinera selon le texte
                        "notes": "Détecté via veille automatique. Vérifier le permis.",
                        "estimated_value": "À chiffrer",
                        "status": "new",
                        "source_url": link, # LIEN POUR VÉRIFIER DE TES YEUX
                        "department": "74"
                    }
                    leads_trouves.append(lead)
        except Exception as e:
            print(f"Erreur sur la requête {query}: {e}")

    # Envoi automatique vers ton SaaS
    if leads_trouves:
        try:
            supabase.table("leads").insert(leads_trouves).execute()
            print(f"✅ {len(leads_trouves)} vrais leads envoyés sur le SaaS !")
        except Exception as e:
            print(f"Erreur envoi Supabase : {e}")
    else:
        print("Aucun nouveau chantier détecté ce matin.")

if __name__ == "__main__":
    scrape_real_leads()
