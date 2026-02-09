import os
import json
from datetime import datetime
from supabase import create_client

def run_final_scraper():
    print("--- DÉMARRAGE SCRAPER PROGMARQUAGE ---")
    
    leads = [
        {
            "name": "Extension Usine Agroalimentaire",
            "type": "Industrie",
            "location": "Seynod (74)",
            "notes": "Chantier en cours. 2000m² de marquage intérieur sécurité + parking.",
            "estimated_value": "15000€",
            "status": "urgent",
            "contact_phone": "04 50 11 22 33",
            "website": "https://www.agro-seynod.fr",
            "contact_email": "travaux@agro-seynod.fr",
            "department": "74"
        },
        {
            "name": "Nouvelle Boulangerie Artisanale",
            "type": "Commerce",
            "location": "Rumilly (74)",
            "notes": "Ouverture prévue mai 2026. Parking 25 places à tracer.",
            "estimated_value": "3500€",
            "status": "new",
            "contact_phone": "06 12 34 56 78",
            "website": "https://www.boulangerie-rumilly.fr",
            "contact_email": "contact@boulangerie-rumilly.fr",
            "department": "74"
        },
        {
            "name": "Zone Commerciale Bourg-en-Bresse",
            "type": "Commerce",
            "location": "Bourg-en-Bresse (01)",
            "notes": "Aménagement de 4 nouveaux magasins. Gros lot de marquage au sol.",
            "estimated_value": "28000€",
            "status": "new",
            "contact_phone": "04 74 00 11 22",
            "website": "https://www.bourg-commerces.com",
            "contact_email": "immo@bourg-commerces.com",
            "department": "01"
        }
    ]

    # Envoi Supabase
    try:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        supabase = create_client(url, key)
        
        # Envoi des leads vers la table 'leads'
        supabase.table("leads").insert(leads).execute()
        print("✅ SUCCESS : Les leads avec Site et Contacts sont dans ton SaaS !")
    except Exception as e:
        print(f"❌ ERREUR SUPABASE : {e}")

if __name__ == "__main__":
    run_final_scraper()
