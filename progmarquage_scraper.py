import os
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from supabase import create_client
import random

def scrape_expert_war_mode():
    print("--- ⚔️ MODE GUERRE TOTALE : EXTRACTION MAXIMALE ---")
    
    # 1. SETUP SUPABASE
    url_supabase = os.environ.get("SUPABASE_URL")
    key_supabase = os.environ.get("SUPABASE_KEY")
    supabase = create_client(url_supabase, key_supabase)

    leads_extraits = []
    
    # Rotation de User-Agents pour éviter d'être banni par Google
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    ]

    # Requêtes ultra-larges pour les 3 derniers mois (73, 74, 01)
    # On cherche l'INTENTION de construire
    queries = [
        "chantier+parking+haute-savoie",
        "permis+construire+entrepot+savoie",
        "amenagement+zone+commerciale+ain",
        "construction+boulangerie+74",
        "nouveau+batiment+industriel+73",
        "marquage+sol+chantier+rhone-alpes"
    ]

    # 2. COLLECTE AGGRESSIVE
    for q in queries:
        print(f"📡 Scan : {q.replace('+', ' ')}")
        url = f"https://news.google.com/search?q={q}+when:3m&hl=fr&gl=FR&ceid=FR:fr"
        
        try:
            res = requests.get(url, headers={'User-Agent': random.choice(user_agents)}, timeout=15)
            soup = BeautifulSoup(res.text, 'html.parser')
            # On cherche tous les liens d'articles
            articles = soup.find_all('article', limit=10)

            for art in articles:
                title_tag = art.find('a', class_='J7YVsc') or art.find('h3')
                if title_tag:
                    title = title_tag.text
                    link = "https://news.google.com" + art.find('a')['href'][1:]
                    
                    leads_extraits.append({
                        "name": title[:120],
                        "type": "PROJET NEUF",
                        "location": "73/74/01",
                        "notes": "Détecté par scan expert. Potentiel marquage au sol élevé.",
                        "estimated_value": "A chiffrer",
                        "status": "new",
                        "source_url": link,
                        "department": "74",
                        "created_at": datetime.now().isoformat()
                    })
        except Exception as e:
            print(f"⚠️ Erreur sur la requête {q}: {e}")

    # 3. SAUVEGARDE FORCÉE (Pour ne plus avoir l'erreur GitHub)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"leads_progmarquage_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(leads_extraits, f, ensure_ascii=False, indent=2)
    print(f"💾 Fichier de secours créé : {filename}")

    # 4. ENVOI SUPABASE
    if leads_extraits:
        try:
            # Suppression des doublons
            unique_leads = {v['name']: v for v in leads_extraits}.values()
            supabase.table("leads").insert(list(unique_leads)).execute()
            print(f"🚀 {len(unique_leads)} leads injectés dans le SaaS !")
        except Exception as e:
            print(f"❌ Erreur d'injection Supabase : {e}")
            print("Vérifie que ta table a bien les colonnes : name, type, location, notes, estimated_value, status, source_url, department")
    else:
        print("Empty: Rien trouvé cette fois-ci.")

if __name__ == "__main__":
    scrape_expert_war_mode()
