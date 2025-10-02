import { useEffect, useState } from "react";
import { api } from "../services/api";

type Alert = {
  id: number;
  cible: string;
  condition: string;
  seuil?: number;
  canal: string;
};

export default function AlertsPanel() {
  const [alertes, setAlertes] = useState<Alert[]>([]);

  useEffect(() => {
    api.get<Alert[]>("/alertes").then((res) => setAlertes(res.data));
  }, []);

  return (
    <section className="rounded-lg bg-white p-4 shadow">
      <h3 className="text-base font-semibold text-slate-800">Alertes actives</h3>
      <ul className="mt-3 space-y-2 text-sm">
        {alertes.map((alerte) => (
          <li key={alerte.id} className="rounded border border-slate-200 px-3 py-2">
            <span className="font-semibold">{alerte.cible}</span> — {alerte.condition}
            {alerte.seuil ? ` ≥ ${alerte.seuil}` : ""} ({alerte.canal})
          </li>
        ))}
        {alertes.length === 0 && <li className="text-slate-500">Aucune alerte configurée.</li>}
      </ul>
    </section>
  );
}
