import { useState } from "react";

export default function SettingsPage() {
  const [email, setEmail] = useState("");
  const [telegram, setTelegram] = useState("");
  const [theme, setTheme] = useState("clair");

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-semibold text-slate-900">Paramètres</h2>
      <form className="space-y-4 rounded-lg bg-white p-5 shadow">
        <div className="grid gap-4 md:grid-cols-2">
          <label className="flex flex-col text-sm text-slate-700">
            Email alertes
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 rounded border border-slate-300 px-3 py-2"
              placeholder="votre.email@example.com"
            />
          </label>
          <label className="flex flex-col text-sm text-slate-700">
            ID chat Telegram
            <input
              value={telegram}
              onChange={(e) => setTelegram(e.target.value)}
              className="mt-1 rounded border border-slate-300 px-3 py-2"
              placeholder="123456789"
            />
          </label>
        </div>
        <label className="flex flex-col text-sm text-slate-700">
          Thème
          <select
            value={theme}
            onChange={(e) => setTheme(e.target.value)}
            className="mt-1 max-w-xs rounded border border-slate-300 px-3 py-2"
          >
            <option value="clair">Clair</option>
            <option value="sombre">Sombre</option>
          </select>
        </label>
        <p className="text-xs text-slate-500">
          Les paramètres sont stockés localement. Configurez les variables d'environnement côté backend pour activer
          l'envoi réel d'alertes.
        </p>
      </form>
    </div>
  );
}
