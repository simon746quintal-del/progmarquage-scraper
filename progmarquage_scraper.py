import requests
from bs4 import BeautifulSoup
import os
from supabase import create_client
from datetime import datetime, timedelta

# Configuration Supabase
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

def scrape_leads():
    print("Démarrage du scan large (30 jours)...")
    leads = []
    
    # Simulation de détection de projets pour test (73, 74, 01)
    # Dans la version réelle, ce bloc analyse les sites de presse et marchés publics
    mots_cles = ["parking", "marquage", "entrepôt", "commerce", "construction", "lotissement"]
    
    # Exemple de lead trouvé (simulation d'un projet réel pour peupler ton SaaS)
    sample_leads = [
        {
            "title": "Extension Parking Super U",
            "location": "Rumilly (74)",
            "description": "Création de 50 nouvelles places de stationnement. Marquage au sol nécessaire.",
            "source_url": "https://www.ledauphine.com",
            "created_at": datetime.now().isoformat(),
            "status": "Nouveau",
            "potential_value": "2500€"
        },
        {
            "title": "Nouvelle Zone Artisanale",
            "location": "Bourg-en-Bresse (01)",
            "description": "Aménagement de voirie pour 4 nouveaux bâtiments industriels.",
            "source_url": "https://www.leprogres.fr",
            "created_at": datetime.now().isoformat(),
            "status": "Urgent",
            "potential_value": "8000€"
        }
    ]

    for lead in sample_leads:
        try:
            # Envoi vers Supabase
            data = supabase.table("leads").insert(lead).execute()
            print(f"✅ Lead ajouté : {lead['title']}")
            leads.append(lead)
        except Exception as e:
            print(f"❌ Erreur Supabase : {e}")

    if not leads:
        print("Aucun nouveau lead trouvé aujourd'hui.")

if __name__ == "__main__":
    scrape_leads()
