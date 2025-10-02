import { useEffect, useState } from "react";
import { api } from "../services/api";
import DataTable from "../components/DataTable";

type Opcvm = {
  id: number;
  code: string;
  nom: string;
  categorie: string;
  societe_gestion?: string;
  periodicite_vl?: string;
  performances: Record<string, number>;
};

export default function OpcvmPage() {
  const [funds, setFunds] = useState<Opcvm[]>([]);
  const [cat, setCat] = useState<string>("");

  useEffect(() => {
    const query = cat ? `?cat=${encodeURIComponent(cat)}` : "";
    api.get<Opcvm[]>(`/opcvm${query}`).then((res) => setFunds(res.data));
  }, [cat]);

  const categories = Array.from(new Set(funds.map((fund) => fund.categorie)));

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <h2 className="text-2xl font-semibold text-slate-900">Fonds OPCVM</h2>
        <select
          className="max-w-xs rounded border border-slate-300 px-2 py-1 text-sm"
          value={cat}
          onChange={(e) => setCat(e.target.value)}
        >
          <option value="">Toutes catégories</option>
          {categories.map((category) => (
            <option key={category} value={category}>
              {category}
            </option>
          ))}
        </select>
      </div>
      <DataTable
        data={funds}
        columns={[
          { key: "code", label: "Code" },
          { key: "nom", label: "Nom" },
          { key: "categorie", label: "Catégorie" },
          {
            key: "performances",
            label: "Perf YTD",
            render: (row) => `${row.performances?.perf_ytd ?? row.performances?.ytd ?? "-"}%`
          },
          {
            key: "performances",
            label: "Perf 3M",
            render: (row) => `${row.performances?.perf_3m ?? row.performances?.["3m"] ?? "-"}%`
          }
        ]}
      />
    </div>
  );
}
