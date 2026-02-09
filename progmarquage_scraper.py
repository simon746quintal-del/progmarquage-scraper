"""
PROGMARQUAGE - SYSTÈME DE SCRAPING AUTOMATIQUE
Détecte automatiquement les nouveaux projets nécessitant du marquage au sol
Régions : Savoie (73), Haute-Savoie (74), Ain (01)
"""

import os
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import json
import re
from supabase import create_client, Client
import time

# Configuration Supabase
SUPABASE_URL = "https://exycahcnbdodqljlcygb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV4eWNhaGNuYmRvZHFsamxjeWdiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzg4NTE2ODUsImV4cCI6MjA1NDQyNzY4NX0.sb_publishable_T0PbuxYkvXzGME4tS9xLCQ_TXs8eO6M"

# Initialiser Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Départements ciblés
DEPARTMENTS = ['73', '74', '01']

# Villes principales par département
CITIES = {
    '73': ['Chambéry', 'Aix-les-Bains', 'Albertville', 'Cognin', 'La Motte-Servolex', 'Bassens', 'Ugine'],
    '74': ['Annecy', 'Annemasse', 'Thonon-les-Bains', 'Cluses', 'Seynod', 'Rumilly', 'Annecy-le-Vieux', 'Cran-Gevrier', 'Sallanches', 'Bonneville', 'Évian-les-Bains'],
    '01': ['Bourg-en-Bresse', 'Oyonnax', 'Bellegarde-sur-Valserine', 'Ambérieu-en-Bugey', 'Ferney-Voltaire', 'Gex', 'Thoiry', 'Divonne-les-Bains']
}

# Types de projets nécessitant du marquage au sol
PROJECT_TYPES = {
    'commerce': ['boulangerie', 'supermarché', 'hypermarché', 'magasin', 'commerce', 'boutique', 'restaurant', 'fast-food', 'café', 'pharmacie', 'opticien'],
    'industrie': ['usine', 'atelier', 'entrepôt', 'plateforme logistique', 'zone industrielle', 'manufacture', 'production'],
    'services': ['garage', 'concession', 'station-service', 'banque', 'cabinet médical', 'clinique', 'cabinet dentaire', 'salle de sport', 'piscine'],
    'hebergement': ['hôtel', 'résidence hôtelière', 'motel', 'apart-hôtel'],
    'loisirs': ['cinéma', 'bowling', 'salle de spectacle', 'centre de loisirs'],
    'bureaux': ['bureaux', 'immeuble de bureaux', 'siège social', 'coworking', 'pépinière d\'entreprises'],
    'residentiel': ['résidence', 'copropriété', 'programme immobilier', 'logements collectifs', 'résidence étudiante', 'résidence senior']
}

# Mots-clés temporels pour identifier les projets RÉCENTS
RECENT_KEYWORDS = [
    'en construction', 'ouverture prévue', 'bientôt', 'projet', 'futur', 
    'à venir', 'permis déposé', 'chantier', 'travaux en cours', 
    'livraison prévue', 'mise en service', 'prochainement',
    'en cours de construction', 'construction en cours', 'va ouvrir',
    'ouvrira', 'sera inauguré', 'annoncé', 'prévu pour', '2026', '2027'
]

# Mots-clés à ÉVITER (projets trop anciens)
OLD_KEYWORDS = [
    'inauguré', 'a ouvert', 'ouvert depuis', 'depuis 2023', 'depuis 2024',
    'fête ses', 'déjà opérationnel', 'en activité depuis', 'célèbre'
]

class ProgMarquageScraper:
    def __init__(self):
        self.leads_found = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def is_recent_project(self, text):
        """Vérifie si le projet est récent (pas déjà ouvert depuis longtemps)"""
        text_lower = text.lower()
        
        # Vérifier les mots-clés d'ancienneté (à éviter)
        for old_keyword in OLD_KEYWORDS:
            if old_keyword in text_lower:
                return False
        
        # Vérifier les mots-clés de récence
        for recent_keyword in RECENT_KEYWORDS:
            if recent_keyword in text_lower:
                return True
        
        # Vérifier les dates futures (2026, 2027)
        current_year = datetime.now().year
        if str(current_year) in text or str(current_year + 1) in text:
            return True
        
        return False

    def extract_project_type(self, text):
        """Identifie le type de projet"""
        text_lower = text.lower()
        for category, keywords in PROJECT_TYPES.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return keyword.capitalize()
        return "Commerce"

    def estimate_value(self, project_type, text):
        """Estime la valeur du projet en fonction du type"""
        text_lower = text.lower()
        
        # Gros projets
        if any(word in text_lower for word in ['centre commercial', 'hypermarché', 'plateforme logistique', 'usine']):
            if any(word in text_lower for word in ['amazon', 'carrefour', 'leclerc', 'auchan']):
                return "35 000 - 50 000 €"
            return "18 000 - 35 000 €"
        
        # Projets moyens
        if any(word in text_lower for word in ['supermarché', 'garage', 'concession', 'entrepôt', 'résidence']):
            return "8 000 - 18 000 €"
        
        # Petits projets
        return "3 000 - 8 000 €"

    def estimate_parking_size(self, project_type, text):
        """Estime la taille du parking"""
        text_lower = text.lower()
        
        # Chercher des chiffres de places mentionnés
        places_match = re.search(r'(\d+)\s*places?', text_lower)
        if places_match:
            return f"{places_match.group(1)} places"
        
        # Estimation par type
        if any(word in text_lower for word in ['hypermarché', 'centre commercial']):
            return "150-300 places"
        if any(word in text_lower for word in ['supermarché', 'grande surface']):
            return "80-150 places"
        if any(word in text_lower for word in ['usine', 'entrepôt', 'plateforme']):
            return "50-200 places (VL + PL)"
        if any(word in text_lower for word in ['résidence', 'copropriété']):
            return "30-80 places"
        
        return "15-40 places"

    def scrape_dauphine_libere(self, department, city):
        """Scrape Le Dauphiné Libéré pour les actualités locales"""
        print(f"🔍 Scraping Le Dauphiné Libéré - {city} ({department})...")
        
        try:
            # URLs de recherche
            search_queries = [
                f"{city} ouverture commerce",
                f"{city} construction magasin",
                f"{city} nouveau commerce",
                f"{city} projet immobilier"
            ]
            
            for query in search_queries:
                url = f"https://www.ledauphine.com/search?q={query.replace(' ', '+')}"
                
                try:
                    response = self.session.get(url, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        articles = soup.find_all('article', limit=5)
                        
                        for article in articles:
                            title = article.find('h2') or article.find('h3')
                            if title:
                                title_text = title.get_text(strip=True)
                                snippet = article.get_text(strip=True)[:500]
                                
                                if self.is_recent_project(snippet):
                                    project_type = self.extract_project_type(snippet)
                                    
                                    lead = {
                                        'name': title_text[:100],
                                        'type': project_type,
                                        'department': department,
                                        'location': f"{city}, {department}",
                                        'source': 'Le Dauphiné Libéré',
                                        'notes': snippet[:300],
                                        'estimated_value': self.estimate_value(project_type, snippet),
                                        'parking_size': self.estimate_parking_size(project_type, snippet),
                                        'status': 'new'
                                    }
                                    
                                    self.leads_found.append(lead)
                                    print(f"  ✅ Lead trouvé: {title_text[:50]}...")
                    
                    time.sleep(2)  # Respecter le serveur
                
                except Exception as e:
                    print(f"  ⚠️ Erreur requête: {e}")
                    continue
        
        except Exception as e:
            print(f"  ❌ Erreur scraping Dauphiné: {e}")

    def scrape_google_news(self, department, city):
        """Scrape Google News pour les actualités locales"""
        print(f"🔍 Scraping Google News - {city} ({department})...")
        
        try:
            queries = [
                f"{city} ouverture commerce 2026",
                f"{city} nouveau magasin",
                f"{city} construction usine",
                f"{city} projet commercial"
            ]
            
            for query in queries:
                url = f"https://news.google.com/search?q={query.replace(' ', '+')}&hl=fr&gl=FR&ceid=FR:fr"
                
                try:
                    response = self.session.get(url, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        articles = soup.find_all('article', limit=5)
                        
                        for article in articles:
                            title = article.find('a')
                            if title:
                                title_text = title.get_text(strip=True)
                                
                                if self.is_recent_project(title_text):
                                    project_type = self.extract_project_type(title_text)
                                    
                                    lead = {
                                        'name': title_text[:100],
                                        'type': project_type,
                                        'department': department,
                                        'location': f"{city}, {department}",
                                        'source': 'Google News',
                                        'notes': f"Projet détecté via Google News: {title_text}",
                                        'estimated_value': self.estimate_value(project_type, title_text),
                                        'parking_size': self.estimate_parking_size(project_type, title_text),
                                        'status': 'new'
                                    }
                                    
                                    self.leads_found.append(lead)
                                    print(f"  ✅ Lead trouvé: {title_text[:50]}...")
                    
                    time.sleep(2)
                
                except Exception as e:
                    print(f"  ⚠️ Erreur requête: {e}")
                    continue
        
        except Exception as e:
            print(f"  ❌ Erreur scraping Google News: {e}")

    def scrape_marches_publics(self, department):
        """Scrape les marchés publics pour les appels d'offres"""
        print(f"🔍 Scraping Marchés Publics - Département {department}...")
        
        try:
            # Simulation de données (à remplacer par vrai scraping de BOAMP)
            # En production, scraper : https://www.boamp.fr
            
            mock_projects = [
                {
                    'name': f'Construction zone commerciale - Département {department}',
                    'type': 'Centre Commercial',
                    'department': department,
                    'location': f'{CITIES[department][0]}, {department}',
                    'source': 'BOAMP - Appel d\'offres public',
                    'notes': 'Appel d\'offres pour marquage au sol zone commerciale',
                    'estimated_value': '25 000 - 40 000 €',
                    'parking_size': '200+ places',
                    'status': 'new'
                }
            ]
            
            # En production, implémenter vrai scraping ici
            print(f"  ℹ️ Marchés publics : à implémenter avec accès API BOAMP")
        
        except Exception as e:
            print(f"  ❌ Erreur scraping Marchés Publics: {e}")

    def add_leads_to_supabase(self):
        """Ajoute les leads trouvés dans Supabase"""
        print(f"\n💾 Ajout de {len(self.leads_found)} leads dans Supabase...")
        
        # Note: Pour la version automatique, il faudrait un user_id système
        # Pour l'instant, on va logger les leads trouvés
        
        for lead in self.leads_found:
            try:
                # En production, ajouter à Supabase avec user_id approprié
                print(f"  ✅ Lead prêt: {lead['name'][:50]}... ({lead['location']})")
                
                # Pour l'instant, juste afficher
                # En production, décommenter:
                # response = supabase.table('leads').insert(lead).execute()
                
            except Exception as e:
                print(f"  ❌ Erreur ajout lead: {e}")

    def run(self):
        """Lance le scraping complet"""
        print("="*80)
        print("🚀 PROGMARQUAGE - SYSTÈME DE SCRAPING AUTOMATIQUE")
        print("="*80)
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Régions: Savoie (73), Haute-Savoie (74), Ain (01)")
        print("="*80)
        
        # Scraper chaque département et ville
        for dept in DEPARTMENTS:
            print(f"\n📍 DÉPARTEMENT {dept}")
            print("-"*80)
            
            for city in CITIES[dept][:3]:  # Limiter à 3 villes par département pour test
                self.scrape_dauphine_libere(dept, city)
                time.sleep(3)
                
                self.scrape_google_news(dept, city)
                time.sleep(3)
            
            self.scrape_marches_publics(dept)
            time.sleep(3)
        
        # Afficher résumé
        print("\n" + "="*80)
        print(f"✅ SCRAPING TERMINÉ - {len(self.leads_found)} LEADS TROUVÉS")
        print("="*80)
        
        # Sauvegarder les leads
        if self.leads_found:
            self.save_leads_to_json()
            # self.add_leads_to_supabase()  # Décommenter en production
        else:
            print("ℹ️ Aucun nouveau lead détecté")

    def save_leads_to_json(self):
        """Sauvegarde les leads dans un fichier JSON"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"leads_progmarquage_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.leads_found, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Leads sauvegardés dans: {filename}")
        
        # Afficher aperçu
        print("\n📋 APERÇU DES LEADS TROUVÉS:")
        print("-"*80)
        for i, lead in enumerate(self.leads_found[:5], 1):
            print(f"{i}. {lead['name'][:60]}")
            print(f"   📍 {lead['location']} | 💰 {lead['estimated_value']}")
            print(f"   🅿️ {lead['parking_size']} | 📰 {lead['source']}")
            print()

if __name__ == "__main__":
    scraper = ProgMarquageScraper()
    scraper.run()
