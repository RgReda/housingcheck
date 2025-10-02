export default function LearnPage() {
  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-semibold text-slate-900">Apprentissage</h2>
      <article className="space-y-3 rounded-lg bg-white p-5 shadow text-sm leading-relaxed text-slate-700">
        <p>
          Cette section synthétise les notions clés issues des ressources éducatives comme Tamra.ma. Nous
          recommandons de comprendre le fonctionnement des indices MASI, MSI20 et MASI ESG, la différence entre les
          OPCVM (actions, obligataire, monétaire) et les métriques de liquidité comme l'ADTV (Average Daily Trading
          Volume).
        </p>
        <p>
          Pour les OPCVM, identifiez la catégorie, la fréquence de publication de la valeur liquidative (VL) et les
          frais d'entrée/sortie. Comparez les performances à différents horizons (YTD, 1M, 3M) pour évaluer la
          régularité du fonds. Les bulletins de la cote et les communiqués AMMC restent les sources officielles pour
          confirmer les informations.
        </p>
        <p>
          Côté actualités, combinez les flux Medias24, L'Économiste, BourseNews et Le Desk afin d'obtenir un panorama
          équilibré entre annonces corporates et analyses sectorielles. Reliez ces événements aux variations de
          prix pour identifier des corrélations pertinentes.
        </p>
      </article>
    </div>
  );
}
