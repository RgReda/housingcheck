import { Outlet, NavLink } from "react-router-dom";
import { useTranslation } from "react-i18next";
import BannerDelay from "./components/BannerDelay";

const navItems = [
  { to: "/", label: "Tableau de bord" },
  { to: "/indices", label: "Indices" },
  { to: "/opcvm", label: "OPCVM" },
  { to: "/news", label: "Actualités" },
  { to: "/apprentissage", label: "Apprentissage" },
  { to: "/parametres", label: "Paramètres" }
];

export default function App() {
  const { t } = useTranslation();
  return (
    <div className="min-h-screen bg-slate-100 text-slate-900">
      <BannerDelay />
      <header className="bg-white shadow">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
          <h1 className="text-lg font-semibold text-primary">{t("app.title")}</h1>
          <nav className="flex gap-4 text-sm">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `rounded px-2 py-1 hover:bg-primary-light/20 focus:outline-none focus:ring ${
                    isActive ? "bg-primary-light/30 text-primary-dark" : ""
                  }`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-6">
        <Outlet />
      </main>
    </div>
  );
}
