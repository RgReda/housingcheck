import axios from "axios";

export const api = axios.create({
  baseURL: "/api"
});

export interface Indice {
  code: string;
  nom: string;
  dernier_niveau?: number;
  variation_jour?: number;
}

export interface ValeurListItem {
  ticker: string;
  nom: string;
  secteur?: string;
  momentum_score?: number;
  adtv?: number;
  news_impact_score?: number;
}

export interface NewsItem {
  id: number;
  titre: string;
  source: string;
  published_at: string;
  url: string;
  news_impact_score?: number;
}
