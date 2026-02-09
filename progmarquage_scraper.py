import os
import json
from datetime import datetime
from supabase import create_client

def run_safe_scraper():
    print("--- DÉMARRAGE DU SCRAPER DE SECOURS ---")
    
    # 1. Données de test forcées
    leads_a_sauver = [
        {
            "name": "TEST : Boulangerie Neuve",
            "type": "Commerce",
            "location": "Rumilly (74)",
            "notes": "Chantier en cours, besoin marquage parking.",
            "estimated_value": "4000€",
            "status": "new"
        }
    ]

    # 2. Création du fichier JSON (Quoi qu'il arrive)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"leads_progmarquage_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(leads_a_sauver, f, ensure_ascii=False, indent=2)
    print(f"✅ Fichier créé : {filename}")

    # 3. Tentative d'envoi Supabase
    try:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        supabase = create_client(url, key)
        # On essaie d'insérer dans 'leads'
        supabase.table("leads").insert(leads_a_sauver).execute()
        print("✅ Données envoyées à Supabase !")
    except Exception as e:
        print(f"⚠️ Erreur Supabase (mais le fichier JSON est sauvé) : {e}")

if __name__ == "__main__":
    run_safe_scraper()
