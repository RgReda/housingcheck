import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import TradingViewWidget from "../components/TradingViewWidget";
import LineOHLC from "../components/LineOHLC";
import { api } from "../services/api";

export default function ValeurPage() {
  const { ticker } = useParams();
  const [detail, setDetail] = useState<any>(null);
  const [mapping, setMapping] = useState<Record<string, string>>({});

  useEffect(() => {
    if (!ticker) return;
    api.get(`/valeurs/${encodeURIComponent(ticker)}`).then((res) => setDetail(res.data));
    fetch("/data/samples/tradingview_symbols.json")
      .then((res) => res.json())
      .then((json) => setMapping(json));
  }, [ticker]);

  const tradingSymbol = useMemo(() => (ticker ? mapping[ticker] ?? ticker : ""), [mapping, ticker]);

  if (!detail) {
    return <p className="text-sm text-slate-500">Chargement…</p>;
  }

  const series = detail.cours.map((c: any) => ({
    time: c.date,
    open: c.open ?? c.close,
    high: c.high ?? c.close,
    low: c.low ?? c.close,
    close: c.close
  }));

  return (
    <div className="space-y-6">
      <div className="rounded-lg bg-white p-6 shadow">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-2xl font-semibold text-slate-900">{detail.nom}</h2>
            <p className="text-sm text-slate-500">{ticker}</p>
          </div>
          <button className="rounded bg-primary px-4 py-2 text-sm text-white shadow hover:bg-primary-dark">
            Créer une alerte
          </button>
        </div>
        <div className="mt-4 grid gap-4 md:grid-cols-4">
          {Object.entries(detail.stats).map(([key, value]) => (
            <div key={key} className="rounded border border-slate-200 p-3 text-sm">
              <p className="text-xs uppercase text-slate-500">{key}</p>
              <p className="text-lg font-semibold">{value ?? "-"}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="rounded-lg bg-white p-4 shadow">
        {mapping[ticker ?? ""] ? <TradingViewWidget symbol={tradingSymbol} /> : <LineOHLC data={series} />}
      </div>

      <section className="rounded-lg bg-white p-4 shadow">
        <h3 className="text-lg font-semibold text-slate-800">Actualités liées</h3>
        <ul className="mt-3 space-y-3 text-sm">
          {detail.latest_news.map((item: any) => (
            <li key={item.url} className="border-b border-slate-200 pb-2 last:border-b-0 last:pb-0">
              <a href={item.url} target="_blank" rel="noreferrer" className="font-medium text-primary">
                {item.titre}
              </a>
              <p className="text-xs text-slate-500">
                {new Date(item.published_at).toLocaleString("fr-FR")} — score {item.news_impact_score ?? "-"}
              </p>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
