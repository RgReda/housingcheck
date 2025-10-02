# SOURCES & LICENCES

| Source | Type | Usage | Notes |
| --- | --- | --- | --- |
| Bourse de Casablanca (cse.ma) | Bulletin PDF, Indices | Bulletin de la cote quotidien, niveaux MASI/MSI20/MASI ESG | Respect des CGU, scraping désactivable via `ENABLE_SCRAPING` |
| Autorité Marocaine du Marché des Capitaux (ammc.ma) | Listes OPCVM | Ingestion des listes agréées | Vérifier les mises à jour officielles avant diffusion |
| Médias24 | RSS / Scraping | Flux d’actualités économiques | Mention de la source obligatoire |
| L’Économiste | RSS / Scraping | Articles macro/sectoriels | Vérifier droits de reproduction |
| BourseNews | RSS / Scraping | News marchés et sociétés cotées | Limiter la fréquence de requêtes |
| Le Desk | RSS | Investigations et dossiers | API publique RSS |
| TradingView | Widget embarqué | Graphiques interactifs | Respect des conditions d’utilisation du widget |
| Telegram Bot API | Notifications | Envoi d’alertes | Nécessite token bot | 
| SMTP (configurable) | Notifications | Email alertes | Requiert serveur compatible |

## Licences logicielles

- Backend : FastAPI (MIT), SQLModel (MIT), APScheduler (BSD).
- Frontend : React (MIT), TailwindCSS (MIT), lightweight-charts (Apache-2.0).
- Outils : pdfplumber (MIT), BeautifulSoup4 (MIT).

## Conformité

- Pas de stockage de données à caractère personnel par défaut.
- Pour l’accès temps réel, une licence spécifique CSE doit être obtenue.
- Les utilisateurs finaux doivent accepter les CGU des sources agrégées.
