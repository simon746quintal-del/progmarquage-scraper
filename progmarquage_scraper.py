import os
import json
from datetime import datetime
from supabase import create_client

def run_final_scraper():
    print("--- DÉMARRAGE SCRAPER PROGMARQUAGE ---")
    
    # Données avec sites et contacts pour tester ton SaaS
    leads = [
        {
            "name": "Extension Usine Agro-Seynod",
            "type": "Industrie",
            "location": "Seynod (74)",
            "notes": "Chantier imminent. 2000m² de marquage intérieur sécurité + parking.",
            "estimated_value": "15000€",
            "status": "urgent",
            "contact_phone": "04 50 11 22 33",
            "website": "https://www.agro-seynod.fr",
            "contact_email": "travaux@agro-seynod.fr",
            "department": "74"
        },
        {
            "name": "Boulangerie Marie Blachère",
            "type": "Commerce",
            "location": "Rumilly (74)",
            "notes": "Nouveau bâtiment. Parking 30 places + zone livraison à tracer.",
            "estimated_value": "4200€",
            "status": "new",
            "contact_phone": "06 12 34 56 78",
            "website": "https://www.marieblachere.com",
            "contact_email": "contact@projet-74.fr",
            "department": "74"
        }
    ]

    # Envoi Supabase
    try:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        supabase = create_client(url, key)
        
        # Insertion dans la table 'leads'
        supabase.table("leads").insert(leads).execute()
        print("✅ SUCCESS : Les leads avec Site et Contacts sont dans ton SaaS !")
    except Exception as e:
        print(f"❌ ERREUR SUPABASE : {e}")

if __name__ == "__main__":
    run_final_scraper()
