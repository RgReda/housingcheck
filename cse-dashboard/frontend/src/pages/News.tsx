import { useEffect, useState } from "react";
import { api, NewsItem } from "../services/api";

export default function NewsPage() {
  const [items, setItems] = useState<NewsItem[]>([]);
  const [source, setSource] = useState<string>("");

  useEffect(() => {
    const query = source ? `?source=${encodeURIComponent(source)}` : "";
    api.get<NewsItem[]>(`/news${query}`).then((res) => setItems(res.data));
  }, [source]);

  const sources = Array.from(new Set(items.map((item) => item.source)));

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <h2 className="text-2xl font-semibold text-slate-900">Actualités agrégées</h2>
        <select
          className="max-w-xs rounded border border-slate-300 px-2 py-1 text-sm"
          value={source}
          onChange={(e) => setSource(e.target.value)}
        >
          <option value="">Toutes sources</option>
          {sources.map((src) => (
            <option key={src} value={src}>
              {src}
            </option>
          ))}
        </select>
      </div>
      <ul className="space-y-4">
        {items.map((item) => (
          <li key={item.id} className="rounded-lg bg-white p-4 shadow">
            <a href={item.url} className="text-lg font-semibold text-primary" target="_blank" rel="noreferrer">
              {item.titre}
            </a>
            <p className="mt-1 text-sm text-slate-500">
              {new Date(item.published_at).toLocaleString("fr-FR")} — {item.source}
            </p>
            <p className="mt-2 text-sm text-slate-700">
              Impact estimé : {Math.round((item.news_impact_score ?? 0) * 100)}%
            </p>
          </li>
        ))}
      </ul>
    </div>
  );
}
