# 🤖 GUIDE COMPLET - SCRAPING AUTOMATIQUE PROGMARQUAGE

## 🎯 CE QUE LE SYSTÈME FAIT

✅ **Détecte automatiquement** les nouveaux projets en Savoie (73), Haute-Savoie (74) et Ain (01)
✅ **Filtre uniquement** les projets RÉCENTS (en construction ou à venir)
✅ **Identifie** tout ce qui nécessite du marquage au sol (parking + intérieur)
✅ **Estime automatiquement** la valeur du projet et la taille du parking
✅ **Ajoute les leads** directement dans votre SaaS
✅ **Tourne 24/7** automatiquement toutes les 6 heures

---

## 📊 SOURCES SCRAPÉES

1. **Le Dauphiné Libéré** → Actualités locales, ouvertures commerciales
2. **Google News** → Annonces de projets, presse locale
3. **Marchés Publics (BOAMP)** → Appels d'offres, gros projets
4. **Sites officiels mairies** → Permis de construire (à venir)

---

## 🔍 CE QUI EST DÉTECTÉ

### Types de projets :
- 🥖 **Commerce** : Boulangerie, supermarché, restaurant, magasin...
- 🏭 **Industrie** : Usine, entrepôt, atelier, plateforme logistique...
- 🚗 **Services** : Garage, station-service, clinique, banque...
- 🏨 **Hébergement** : Hôtel, résidence hôtelière...
- 🎬 **Loisirs** : Cinéma, bowling, salle de sport...
- 🏢 **Bureaux** : Immeubles, sièges sociaux...
- 🏘️ **Résidentiel** : Résidences, copropriétés (parking collectif)

### Filtres temporels :
- ✅ **EN CONSTRUCTION** actuellement
- ✅ **OUVERTURE PRÉVUE** dans les 3-6 mois
- ✅ **PERMIS RÉCENT** (< 6 mois)
- ✅ **PROJET ANNONCÉ** pour 2026-2027
- ❌ **DÉJÀ OUVERT** depuis > 2 mois (ÉLIMINÉ)

---

## 🚀 INSTALLATION - 3 OPTIONS

### **OPTION 1 : GitHub Actions (RECOMMANDÉ - 100% GRATUIT & AUTO)**

C'est la solution la plus simple ! GitHub va exécuter le scraper automatiquement pour vous.

#### Étapes :

1. **Créez un compte GitHub** (si pas déjà fait) : https://github.com

2. **Créez un nouveau repository** :
   - Nom : `progmarquage-scraper`
   - Visibilité : Private

3. **Uploadez les fichiers** :
   - `progmarquage_scraper.py`
   - `requirements.txt`
   - `.github/workflows/auto-scraper.yml`

4. **Configurez les secrets** :
   - Allez dans `Settings` > `Secrets and variables` > `Actions`
   - Cliquez `New repository secret`
   - Ajoutez :
     - `SUPABASE_URL` = `https://exycahcnbdodqljlcygb.supabase.co`
     - `SUPABASE_KEY` = `votre_clé_supabase`

5. **Activez GitHub Actions** :
   - Allez dans l'onglet `Actions`
   - Activez les workflows

6. **Lancez le premier scraping** :
   - Dans `Actions` > `ProgMarquage Auto Scraper`
   - Cliquez `Run workflow`

✅ **C'EST TOUT !** Le scraper tournera maintenant automatiquement toutes les 6 heures !

---

### **OPTION 2 : Serveur Cloud Gratuit (Render.com)**

Pour exécuter le scraper sur un serveur dédié.

#### Étapes :

1. **Créez un compte** sur https://render.com

2. **Créez un nouveau Cron Job** :
   - Type : Cron Job
   - Repository : Votre repo GitHub
   - Build Command : `pip install -r requirements.txt`
   - Command : `python progmarquage_scraper.py`
   - Schedule : `0 */6 * * *` (toutes les 6h)

3. **Ajoutez les variables d'environnement** :
   - `SUPABASE_URL`
   - `SUPABASE_KEY`

✅ Le scraper tournera automatiquement sur Render !

---

### **OPTION 3 : En local sur votre ordinateur**

Pour tester ou exécuter manuellement.

#### Étapes :

1. **Installez Python 3.11** : https://www.python.org/downloads/

2. **Installez les dépendances** :
```bash
pip install -r requirements.txt
```

3. **Lancez le scraper** :
```bash
python progmarquage_scraper.py
```

4. **Pour automatiser** (Windows) :
   - Utilisez le Planificateur de tâches Windows
   - Créez une tâche qui lance le script toutes les 6h

---

## 📋 MODIFICATION DU SCRIPT POUR AJOUT AUTO À SUPABASE

Pour que les leads soient **automatiquement ajoutés** dans votre SaaS :

### Dans `progmarquage_scraper.py`, ligne 317 :

**AVANT (version test) :**
```python
# Pour l'instant, juste afficher
# En production, décommenter:
# response = supabase.table('leads').insert(lead).execute()
```

**APRÈS (version production) :**
```python
# Ajout automatique dans Supabase
response = supabase.table('leads').insert(lead).execute()
print(f"  ✅ Lead ajouté à Supabase: {lead['name'][:50]}")
```

⚠️ **PROBLÈME** : Il faut un `user_id` pour Supabase RLS.

### SOLUTION : Créer un utilisateur "système"

1. Dans Supabase, créez un compte email : `scraper@progmarquage.fr`
2. Récupérez son `user_id` dans la table `auth.users`
3. Ajoutez ce `user_id` à tous les leads automatiques

**OU MIEUX** : Modifier la politique RLS pour permettre l'insertion sans user_id pour un service account.

---

## 🔧 AMÉLIORER LE SCRAPING

### Ajouter plus de sources :

1. **Permis de construire officiels** :
   - Sites des mairies
   - Registres publics

2. **Réseaux sociaux** :
   - Facebook (pages de zones commerciales)
   - LinkedIn (annonces d'entreprises)

3. **Sites immobiliers** :
   - SeLoger, LeBonCoin (commerces à louer/vendre)

4. **APIs gouvernementales** :
   - data.gouv.fr
   - API cadastre

---

## 📧 AJOUTER DES ALERTES EMAIL

Pour recevoir un email quand un lead urgent est détecté :

### Installer SendGrid (gratuit 100 emails/jour) :

```bash
pip install sendgrid
```

### Ajouter dans le code :

```python
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_alert_email(lead):
    message = Mail(
        from_email='scraper@progmarquage.fr',
        to_emails='votre-email@progmarquage.fr',
        subject=f'🚨 LEAD URGENT : {lead["name"]}',
        html_content=f'''
            <h2>Nouveau lead détecté !</h2>
            <p><strong>{lead["name"]}</strong></p>
            <p>📍 {lead["location"]}</p>
            <p>💰 {lead["estimated_value"]}</p>
            <p>🅿️ {lead["parking_size"]}</p>
        '''
    )
    
    sg = SendGridAPIClient('VOTRE_API_KEY_SENDGRID')
    sg.send(message)
```

---

## 📊 STATISTIQUES & MONITORING

### Voir combien de leads sont scrapés :

Le script génère un fichier JSON après chaque exécution :
- `leads_progmarquage_20260209_143022.json`

Vous pouvez consulter ces fichiers pour voir tous les leads détectés.

---

## 🐛 RÉSOLUTION DE PROBLÈMES

### Le scraper ne trouve aucun lead :
➡️ Normal si pas de nouveaux projets annoncés récemment
➡️ Attendez quelques jours, le scraper continuera à tourner

### Erreur "Rate limit exceeded" :
➡️ Le site bloque trop de requêtes
➡️ Augmentez le `time.sleep()` entre les requêtes

### Les leads ne s'ajoutent pas à Supabase :
➡️ Vérifiez les permissions RLS
➡️ Vérifiez que le `user_id` est correct

---

## 🎯 PROCHAINES ÉTAPES

1. ✅ **Tester le scraper** manuellement
2. ✅ **Déployer sur GitHub Actions** pour automatisation
3. ✅ **Vérifier** que les leads apparaissent dans votre SaaS
4. 🚀 **Ajouter plus de sources** (permis de construire, etc.)
5. 📧 **Configurer les alertes email** pour les leads urgents

---

## ✅ CHECKLIST DÉPLOIEMENT

- [ ] Script `progmarquage_scraper.py` créé
- [ ] Dépendances installées (`requirements.txt`)
- [ ] Repository GitHub créé
- [ ] Secrets configurés dans GitHub
- [ ] Workflow GitHub Actions activé
- [ ] Premier scraping testé manuellement
- [ ] Leads vérifiés dans le SaaS
- [ ] Scraping automatique activé (toutes les 6h)

---

## 🎉 FÉLICITATIONS !

Votre système de scraping automatique est maintenant opérationnel ! Vous allez recevoir automatiquement tous les nouveaux projets nécessitant du marquage au sol en Savoie, Haute-Savoie et Ain ! 🚀🔥

---

## 📞 SUPPORT

En cas de problème, vérifiez :
1. Les logs dans GitHub Actions
2. Les fichiers JSON générés
3. Les permissions Supabase
