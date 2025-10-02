import { useEffect, useMemo, useState } from "react";
import { api, Indice, ValeurListItem, NewsItem } from "../services/api";
import DataTable from "../components/DataTable";
import AlertsPanel from "../components/AlertsPanel";
import TradingViewWidget from "../components/TradingViewWidget";
import LineOHLC from "../components/LineOHLC";

interface SeriePoint {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
}

export default function Dashboard() {
  const [indices, setIndices] = useState<Indice[]>([]);
  const [valeurs, setValeurs] = useState<ValeurListItem[]>([]);
  const [news, setNews] = useState<NewsItem[]>([]);
  const [selectedTicker, setSelectedTicker] = useState<string>("CSE:ATW");
  const [series, setSeries] = useState<SeriePoint[]>([]);
  const [mapping, setMapping] = useState<Record<string, string>>({});

  useEffect(() => {
    api.get<Indice[]>("/indices").then((res) => setIndices(res.data));
    api.get<ValeurListItem[]>("/valeurs").then((res) => {
      setValeurs(res.data);
      if (res.data.length) {
        setSelectedTicker(res.data[0].ticker);
      }
    });
    api.get<NewsItem[]>("/news").then((res) => setNews(res.data.slice(0, 5)));
    fetch("/data/samples/tradingview_symbols.json")
      .then((res) => res.json())
      .then((json) => setMapping(json));
  }, []);

  useEffect(() => {
    if (!selectedTicker) return;
    api.get(`/valeurs/${encodeURIComponent(selectedTicker)}`).then((res) => {
      const data = res.data.cours.map((c: any) => ({
        time: c.date,
        open: c.open ?? c.close,
        high: c.high ?? c.close,
        low: c.low ?? c.close,
        close: c.close
      }));
      setSeries(data);
    });
  }, [selectedTicker]);

  const tradingSymbol = useMemo(() => mapping[selectedTicker] ?? selectedTicker, [mapping, selectedTicker]);

  return (
    <div className="space-y-6">
      <section className="grid gap-4 md:grid-cols-4">
        {indices.map((indice) => (
          <div key={indice.code} className="rounded-lg bg-white p-4 shadow">
            <p className="text-xs uppercase text-slate-500">{indice.nom}</p>
            <p className="text-2xl font-semibold">{indice.dernier_niveau?.toLocaleString("fr-FR")}</p>
            <p className={`text-sm ${indice.variation_jour && indice.variation_jour >= 0 ? "text-green-600" : "text-red-600"}`}>
              {indice.variation_jour?.toFixed(2)}%
            </p>
          </div>
        ))}
      </section>

      <section className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-800">Graphiques</h2>
            <select
              className="rounded border border-slate-300 px-2 py-1 text-sm"
              value={selectedTicker}
              onChange={(e) => setSelectedTicker(e.target.value)}
            >
              {valeurs.map((valeur) => (
                <option key={valeur.ticker} value={valeur.ticker}>
                  {valeur.nom}
                </option>
              ))}
            </select>
          </div>
          <div className="rounded-lg bg-white p-4 shadow">
            {mapping[selectedTicker] ? (
              <TradingViewWidget symbol={tradingSymbol} />
            ) : (
              <LineOHLC data={series} />
            )}
          </div>
        </div>
        <div className="space-y-4">
          <section className="rounded-lg bg-white p-4 shadow">
            <h3 className="text-base font-semibold text-slate-800">Actualités récentes</h3>
            <ul className="mt-3 space-y-3 text-sm">
              {news.map((item) => (
                <li key={item.id} className="border-b border-slate-200 pb-2 last:border-b-0 last:pb-0">
                  <a href={item.url} className="font-medium text-primary" target="_blank" rel="noreferrer">
                    {item.titre}
                  </a>
                  <p className="text-xs text-slate-500">
                    {new Date(item.published_at).toLocaleString("fr-FR")} — {item.source}
                  </p>
                </li>
              ))}
            </ul>
          </section>
          <AlertsPanel />
        </div>
      </section>

      <section className="rounded-lg bg-white p-4 shadow">
        <h3 className="text-lg font-semibold text-slate-800">Idées à privilégier</h3>
        <DataTable
          data={valeurs.slice(0, 5)}
          columns={[
            { key: "nom", label: "Valeur" },
            { key: "momentum_score", label: "Momentum 3M", render: (row) => row.momentum_score?.toFixed(2) ?? "-" },
            { key: "adtv", label: "ADTV", render: (row) => row.adtv?.toLocaleString("fr-FR") ?? "-" },
            {
              key: "news_impact_score",
              label: "Impact news",
              render: (row) => `${Math.round((row.news_impact_score ?? 0) * 100)}%`
            }
          ]}
        />
      </section>
    </div>
  );
}
