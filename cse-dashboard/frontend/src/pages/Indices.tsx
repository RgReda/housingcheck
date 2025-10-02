import { useEffect, useState } from "react";
import { api, Indice } from "../services/api";

export default function IndicesPage() {
  const [indices, setIndices] = useState<Indice[]>([]);

  useEffect(() => {
    api.get<Indice[]>("/indices").then((res) => setIndices(res.data));
  }, []);

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-semibold text-slate-900">Indices principaux</h2>
      <div className="grid gap-4 md:grid-cols-3">
        {indices.map((indice) => (
          <div key={indice.code} className="rounded-lg bg-white p-4 shadow">
            <p className="text-xs uppercase text-slate-500">{indice.code}</p>
            <p className="text-xl font-semibold">{indice.dernier_niveau?.toLocaleString("fr-FR")}</p>
            <p className={`text-sm ${indice.variation_jour && indice.variation_jour >= 0 ? "text-green-600" : "text-red-600"}`}>
              {indice.variation_jour?.toFixed(2)}%
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
