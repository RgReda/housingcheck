import { useTranslation } from "react-i18next";

export default function BannerDelay() {
  const { t } = useTranslation();
  return (
    <div className="bg-yellow-100 text-yellow-900">
      <div className="mx-auto max-w-6xl px-4 py-2 text-center text-sm">
        {t("dashboard.delay")} — aucune licence temps réel configurée.
      </div>
    </div>
  );
}
