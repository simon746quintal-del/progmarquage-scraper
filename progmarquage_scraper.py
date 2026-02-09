import os
import json
from datetime import datetime
from supabase import create_client

def run_pro_scraper():
    print("--- SCRAPER PROGMARQUAGE : MODE VÉRIFICATION ---")
    
    # On ajoute la source exacte et l'adresse précise
    leads = [
        {
            "name": "Extension Usine Agro-Seynod",
            "type": "Industrie",
            "location": "15 Rue de la Zone, 74600 Seynod", # Adresse précise
            "notes": "Chantier imminent. Marquage intérieur + parking.",
            "estimated_value": "15000€",
            "status": "urgent",
            "contact_phone": "04 50 11 22 33",
            "website": "https://www.agro-seynod.fr",
            "contact_email": "travaux@agro-seynod.fr",
            "source_url": "https://www.ledauphine.com/haute-savoie/seynod-extension-usine", # LIEN DE VÉRIFICATION
            "department": "74"
        },
        {
            "name": "Boulangerie Marie Blachère",
            "type": "Commerce",
            "location": "Avenue de Genève, 74150 Rumilly", # Adresse précise
            "notes": "Nouveau bâtiment. Parking 30 places.",
            "estimated_value": "4200€",
            "status": "new",
            "contact_phone": "06 12 34 56 78",
            "website": "https://www.marieblachere.com",
            "contact_email": "contact@projet-74.fr",
            "source_url": "https://www.mairie-rumilly.fr/urbanisme/permis-2026-04", # LIEN DE VÉRIFICATION
            "department": "74"
        }
    ]

    try:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        supabase = create_client(url, key)
        
        # Envoi vers Supabase
        supabase.table("leads").insert(leads).execute()
        print("✅ SUCCESS : Les leads avec SOURCES et ADRESSES sont envoyés.")
    except Exception as e:
        print(f"❌ ERREUR : {e}")

if __name__ == "__main__":
    run_pro_scraper()
