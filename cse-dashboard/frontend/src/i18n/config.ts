import i18n from "i18next";
import { initReactI18next } from "react-i18next";

const resources = {
  fr: {
    translation: {
      "app.title": "Tableau de bord Bourse de Casablanca",
      "dashboard.delay": "Cours différés ~15 min (public)",
      "dashboard.topIdeas": "Idées à privilégier",
      "dashboard.watchlist": "Ma watchlist",
      "settings.title": "Paramètres",
      "learn.title": "Zone d'apprentissage"
    }
  }
};

i18n.use(initReactI18next).init({
  resources,
  lng: "fr",
  interpolation: {
    escapeValue: false
  }
});

export default i18n;
