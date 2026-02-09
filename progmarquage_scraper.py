import os
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from supabase import create_client
import time

def scrape_ultra_massive():
    print("--- 🛰️ DÉMARRAGE DU SCRAPER MASSIF : OBJECTIF 100% LEADS ---")
    
    url_supabase = os.environ.get("SUPABASE_URL")
    key_supabase = os.environ.get("SUPABASE_KEY")
    supabase = create_client(url_supabase, key_supabase)

    all_leads = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    # 1. LISTE DE RECHERCHE GÉANTE (3 derniers mois + Secteurs clés)
    # On ratisse TOUT ce qui nécessite du marquage au sol
    search_matrix = [
        # SECTEUR COMMERCE
        "nouveau+commerce+ouverture+2025+2026+haute-savoie",
        "projet+boulangerie+neuve+savoie+73",
        "construction+supermarché+lidl+aldi+74",
        "centre+commercial+extension+ain+01",
        # SECTEUR INDUSTRIE & LOGISTIQUE (Gros chantiers)
        "permis+construire+entrepôt+logistique+74",
        "plateforme+logistique+construction+savoie",
        "extension+usine+zone+industrielle+ain",
        "parc+d+activité+nouveau+haute-savoie",
        # SECTEUR RÉSIDENTIEL & COLLECTIF
        "programme+immobilier+neuf+parking+annecy",
        "résidence+étudiante+construction+chambéry",
        "copropriété+neuve+parking+souterrain+74",
        # SECTEUR SERVICES & LOISIRS
        "nouveau+garage+automobile+73+74",
        "construction+salle+de+sport+fitness+ain",
        "clinique+ehpad+nouveau+projet+savoie"
    ]

    # 2. MOTEUR DE COLLECTE
    for query in search_matrix:
        print(f"🔍 Scan profond : {query.replace('+', ' ')}")
        # On utilise le paramètre 'when:3m' pour les 3 derniers mois si disponible via URL
        google_url = f"https://news.google.com/search?q={query}&hl=fr&gl=FR&ceid=FR:fr"
        
        try:
            page = requests.get(google_url, headers=headers, timeout=20)
            soup = BeautifulSoup(page.text, 'html.parser')
            articles = soup.find_all('article', limit=15) # On passe à 15 résultats par requête

            for art in articles:
                titre_elem = art.find('a', class_='J7YVsc') or art.find('h3')
                if titre_elem:
                    titre = titre_elem.text
                    link_elem = art.find('a')
                    lien = "https://news.google.com" + link_elem['href'][1:] if link_elem else "Lien indisponible"
                    
                    # Intelligence de tri par département
                    dept = "74"
                    if any(x in titre.lower() for x in ["73", "savoie", "chambéry", "aix"]): dept = "73"
                    elif any(x in titre.lower() for x in ["01", "ain", "bourg", "oyonnax"]): dept = "01"

                    # Nettoyage et typage
                    all_leads.append({
                        "name": titre[:120],
                        "type": "Chantier / Projet Neuf",
                        "location": f"Secteur {dept}",
                        "notes": "Détecté par scan massif 3 mois. Cliquer sur la source pour l'adresse.",
                        "estimated_value": "À chiffrer",
                        "status": "new",
                        "source_url": lien,
                        "department": dept,
                        "created_at": datetime.now().isoformat()
                    })
            time.sleep(1) # Pause pour éviter le blocage
        except Exception as e:
            print(f"Erreur sur {query}: {e}")

    # 3. FILTRAGE DES DOUBLONS (Basé sur le titre)
    unique_leads = {v['name']: v for v in all_leads}.values()
    final_list = list(unique_leads)

    # 4. SAUVEGARDE ET EXPORT
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    with open(f"leads_massive_{timestamp}.json", 'w', encoding='utf-8') as f:
        json.dump(final_list, f, ensure_ascii=False, indent=2)

    if final_list:
        try:
            # Envoi par paquets vers Supabase pour éviter les erreurs de timeout
            chunk_size = 50
            for i in range(0, len(final_list), chunk_size):
                chunk = final_list[i:i + chunk_size]
                supabase.table("leads").insert(chunk).execute()
            print(f"✅ MISSION RÉUSSIE : {len(final_list)} leads uniques envoyés au SaaS !")
        except Exception as e:
            print(f"Erreur Supabase : {e}")
    else:
        print("⚠️ Aucun résultat trouvé malgré le scan massif.")

if __name__ == "__main__":
    scrape_ultra_massive()
