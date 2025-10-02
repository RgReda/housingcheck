# Tableau de bord Bourse de Casablanca

## Contexte & Intentions

Parfait, je vais lancer une recherche approfondie pour concevoir un tableau de bord web personnel sur la Bourse de Casablanca, avec données en temps réel, alertes personnalisées, contenu éducatif, et couverture complète (actions, OPCVM, indices, actualités). Je vais aussi analyser les ressources proposées sur tamra.ma et les meilleures sources fiables marocaines comme BourseNews, L’Économiste, Le Desk et Médias24. Je reviens vers toi bientôt avec une proposition détaillée.

Parfait. Passons “mode étude” et faisons une synthèse profonde de toutes les sources que nous avons mobilisées, puis tirons-en des décisions concrètes pour améliorer ton agent (données, temps réel, news, OPCVM, graphes, alertes). Dis-moi à la fin une seule chose: tu préfères que je priorise l’intégration graphiques TradingView ou la connexion à une source temps réel payante ? (choisis l’un des deux)

### Analyse structurée

- **Sources officielles CSE/AMMC** : exploitation des Bulletins de la cote (PDF) et des listes AMMC pour les OPCVM. Les endpoints `/api/refresh/daily-close` et le job planifié ré-ingèrent ces documents pour garantir une fiabilité quotidienne.
- **News Médias24 / L’Économiste / BourseNews / Le Desk** : agrégées via adaptateurs RSS/Scraping modulaires, stockées en base avec détection de tickers et score d’impact.
- **Partenariat TradingView** : intégration native du widget lorsque le symbole CSE est supporté, avec fallback lightweight-charts si absent.
- **Contraintes “D+15” en public** : bandeau d’avertissement affiché dans l’interface, et simulateur intraday pour les environnements sans licence temps réel.
- **Recommandations ingestion** : jobs APScheduler (2-5 min intraday, 15 min news, 17h30 bulletin) et service d’ingestion échantillonné prêt pour substitution par flux réels.
- **Corrélations news ↔ prix** : calcul du `news_impact_score` et stockage dans `SignalMomentum` pour alimenter le scoring court/moyen terme.
- **OPCVM** : modèle `OPCVM` + `ValeurLiquidative`, filtres par catégorie, tri par performances dans l’UI.
- **Roadmap** : ajout futur d’authentification, branchement à flux temps réel licencié, enrichissement NLP (classification tonalité), automatisation reporting PDF.
- **Limites / licences** : aucun flux temps réel propriétaire fourni, respect strict des CGU des sites sources ; variables d’environnement pour désactiver le scraping.
- **Glossaire** : voir `docs/GLOSSAIRE.md` pour les définitions MASI, MSI20, OPCVM, ADTV, etc.

## Architecture du dépôt

Le monorepo est organisé selon les exigences : backend FastAPI, frontend Vite/React, données d’exemple, documentation et scripts de déploiement Docker.

```
cse-dashboard/
├─ backend/ (FastAPI + SQLModel + APScheduler)
├─ frontend/ (React + TypeScript + TailwindCSS)
├─ data/ (échantillons JSON + bulletin PDF)
├─ docs/ (présent document, SOURCES, GLOSSAIRE)
├─ deploy/ (Dockerfiles + docker-compose)
├─ Makefile, requirements.txt, .env.example, .gitignore
```

## Démarrage rapide

### Pré-requis

- Python 3.11+
- Node.js 20+
- Docker (optionnel pour la conteneurisation)

### Installation locale

```bash
cd cse-dashboard
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd frontend && npm install
```

### Lancement en développement

Dans deux terminaux :

```bash
make backend-dev
# et
cd frontend
npm run dev
```

- API : http://localhost:8000/docs
- Frontend : http://localhost:5173

### Docker Compose

```bash
cd cse-dashboard
make up
```

### Jeux de données d’exemple

Le script `make seed` alimente la base SQLite à partir de `data/samples`. Les fichiers JSON et `bulletin_sample.pdf` garantissent un fonctionnement hors-ligne.

### Configuration détaillée (.env)

Copiez `.env.example` vers `.env` à la racine du dépôt et complétez les variables suivantes avant un déploiement :

| Variable | Obligatoire | Description |
| --- | --- | --- |
| `ENVIRONMENT` | Oui | `development`, `staging` ou `production` pour piloter le niveau de logs. |
| `DATABASE_URL` | Oui | Chaîne SQLModel/SQLAlchemy. Exemple : `sqlite:///./cse_dashboard.db` en local ou `postgresql+psycopg://user:pass@host:5432/dbname` en production. |
| `SMTP_HOST` / `SMTP_PORT` / `SMTP_USER` / `SMTP_PASSWORD` | Requis pour l’envoi d’e-mails | Renseignez l’hôte SMTP autorisé (par ex. `smtp.sendgrid.net`), le port (souvent `587`), l’utilisateur et le mot de passe/API key. Sans ces valeurs, le module d’alertes e-mail est désactivé automatiquement. |
| `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` | Requis pour alertes Telegram | Créez un bot via `@BotFather`, récupérez le token et indiquez l’identifiant du salon ou de l’utilisateur cible (via `getUpdates`). Si l’un manque, l’envoi Telegram est ignoré. |
| `ENABLE_SCRAPING` | Oui (défaut `true`) | Permet de désactiver toute collecte distante pour un environnement soumis à des restrictions réseau/licence. |
| `LEGAL_DELAY_BANNER` | Oui | Doit rester à `true` tant que vous n’avez pas souscrit à un flux temps réel licencié ; masque obligatoire “Cours différés ~15 min (public)”. |
| `TRADINGVIEW_SYMBOLS_MAPPING_FILE` | Oui | Fichier JSON contenant le mapping CSE → symboles TradingView. Laisser la valeur par défaut pour les démos hors-ligne. |
| `DAILY_CLOSE_PDF_PATH` | Oui | Chemin vers le bulletin PDF utilisé par le job `daily-close`. Remplacez-le par un stockage partagé ou un téléchargement automatisé en production. |

Astuce : pour Docker Compose, ajoutez un fichier `deploy/.env` avec les mêmes clés ; `docker-compose.yml` charge automatiquement ce fichier si présent.

## Tests & Qualité

- `make lint` : Ruff + Black + mypy
- `make test` : Pytest (API + parsing PDF)
- Pré-commit configuré via `pre-commit-config.yaml`
- CI GitHub Actions (fichier `.github/workflows/ci.yml`) exécute lint + tests

## Sécurité & conformité

- Mention obligatoire “Cours différés ~15 min (public)” affichée côté frontend.
- Variables `.env` pour activer SMTP/Telegram, désactiver le scraping ou pointer vers des flux sous licence.
- Logging JSON pour les jobs et scrapers afin d’auditer les accès.

## Roadmap

- Authentification multi-utilisateur et profils d’alertes persistants.
- Intégration d’un fournisseur temps réel sous licence.
- Enrichissement NLP (classification sentiment/tendance).
- Génération automatique de rapports quotidiens PDF.

## Limites connues

- Données intraday simulées en l’absence de licence.
- Scrapers RSS susceptibles d’échecs réseau (backoff implémenté, mais supervision requise).
- Pas d’orchestration multi-nœuds pour APScheduler (prévoir un scheduler dédié en production).

## Sources & Licences

Voir `docs/SOURCES.md` pour la liste complète des flux, CGU et restrictions d’usage.
