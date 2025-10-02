import React from "react";
import ReactDOM from "react-dom/client";
import { RouterProvider, createBrowserRouter } from "react-router-dom";
import App from "./App";
import Dashboard from "./pages/Dashboard";
import ValeurPage from "./pages/Valeur";
import IndicesPage from "./pages/Indices";
import OpcvmPage from "./pages/Opcvm";
import NewsPage from "./pages/News";
import LearnPage from "./pages/Learn";
import SettingsPage from "./pages/Settings";
import "./index.css";
import "./i18n/config";

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: "valeur/:ticker", element: <ValeurPage /> },
      { path: "indices", element: <IndicesPage /> },
      { path: "opcvm", element: <OpcvmPage /> },
      { path: "news", element: <NewsPage /> },
      { path: "apprentissage", element: <LearnPage /> },
      { path: "parametres", element: <SettingsPage /> }
    ]
  }
]);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);
