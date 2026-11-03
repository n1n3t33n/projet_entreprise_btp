import {
  Bell,
  CheckCircle,
  Circle,
  ClipboardText,
  Clock,
  GearSix,
  Gauge,
  House,
  type Icon as PhosphorIcon,
  Package,
  Users,
  Warehouse,
  Warning,
  WarningOctagon,
} from '@phosphor-icons/react'
import type { ReactNode } from 'react'

type Swatch = {
  nom: string
  role: string
  hex: string
  bgClass: string
  sombre?: boolean
}

type Statut = {
  libelle: string
  icone: PhosphorIcon
  pilule: string
}

type IconeCatalogue = {
  composant: PhosphorIcon
  libelle: string
}

const marque: Swatch[] = [
  {
    nom: 'Primaire · marine',
    role: 'Navigation, boutons, titres',
    hex: '#002E5E',
    bgClass: 'bg-marine',
    sombre: true,
  },
  {
    nom: 'Secondaire · sarcelle',
    role: 'Liens, accents interactifs',
    hex: '#1F7FA8',
    bgClass: 'bg-sarcelle',
    sombre: true,
  },
  {
    nom: 'Accent · or',
    role: 'Alertes de seuil, badges',
    hex: '#8A6508',
    bgClass: 'bg-or',
    sombre: true,
  },
  { nom: 'Or clair', role: 'Fonds de badge', hex: '#FBF1CF', bgClass: 'bg-or-clair' },
  { nom: 'Or vif', role: 'Surbrillance de sélection', hex: '#F6DF94', bgClass: 'bg-or-vif' },
]

const fonds: Swatch[] = [
  { nom: 'Fond', role: 'Arrière-plan de page', hex: '#F3F8FC', bgClass: 'bg-fond' },
  { nom: 'Fond secondaire', role: 'Fonds de section', hex: '#EAF6FC', bgClass: 'bg-fond-alt' },
  { nom: 'Surface', role: 'Cartes', hex: '#FFFFFF', bgClass: 'bg-surface' },
  { nom: 'Bordure', role: 'Séparateurs', hex: '#E3EDF5', bgClass: 'bg-bordure' },
]

const textes: Swatch[] = [
  {
    nom: 'Texte principal',
    role: 'Corps, intitulés',
    hex: '#2B3A4A',
    bgClass: 'bg-texte',
    sombre: true,
  },
  {
    nom: 'Texte secondaire',
    role: 'Sous-titres, légendes',
    hex: '#5A6572',
    bgClass: 'bg-texte-secondaire',
    sombre: true,
  },
  {
    nom: 'Texte atténué',
    role: 'Mentions discrètes',
    hex: '#9AA5B1',
    bgClass: 'bg-texte-attenue',
    sombre: true,
  },
]

const etats: Swatch[] = [
  {
    nom: 'Succès',
    role: 'Validation, conformité',
    hex: '#2E7D32',
    bgClass: 'bg-succes',
    sombre: true,
  },
  {
    nom: 'Danger',
    role: 'Blocage, état critique',
    hex: '#C0392B',
    bgClass: 'bg-danger',
    sombre: true,
  },
]

const statuts: Statut[] = [
  { libelle: 'À faire', icone: Circle, pilule: 'bg-fond-alt text-texte-secondaire' },
  { libelle: 'En cours', icone: Clock, pilule: 'bg-fond-alt text-marine' },
  { libelle: 'Terminée', icone: CheckCircle, pilule: 'bg-succes/10 text-succes' },
  { libelle: 'En retard', icone: Warning, pilule: 'bg-or-clair text-or' },
  { libelle: 'Critique', icone: WarningOctagon, pilule: 'bg-danger/10 text-danger' },
]

const icones: IconeCatalogue[] = [
  { composant: House, libelle: 'Accueil' },
  { composant: Package, libelle: 'Articles' },
  { composant: Warehouse, libelle: 'Magasins' },
  { composant: ClipboardText, libelle: 'Fiches de route' },
  { composant: Gauge, libelle: 'Seuils' },
  { composant: Bell, libelle: 'Alertes' },
  { composant: Users, libelle: 'Comptes' },
  { composant: GearSix, libelle: 'Paramètres' },
]

function Section({ titre, children }: { titre: string; children: ReactNode }) {
  return (
    <section className="space-y-4">
      <h2 className="text-xl font-bold text-marine">{titre}</h2>
      {children}
    </section>
  )
}

function GroupeCouleurs({ titre, nuances }: { titre: string; nuances: Swatch[] }) {
  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold text-texte-secondaire">{titre}</h3>
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
        {nuances.map((n) => (
          <div
            key={n.nom}
            className="overflow-hidden rounded-controle border border-bordure bg-surface shadow-douce"
          >
            <div
              className={`flex h-20 items-end justify-end p-2 ${n.bgClass} ${n.sombre ? 'text-white' : 'text-texte'}`}
            >
              <span className="font-mono text-xs">{n.hex}</span>
            </div>
            <div className="space-y-0.5 p-3">
              <p className="text-sm font-semibold">{n.nom}</p>
              <p className="text-xs text-texte-secondaire">{n.role}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export function DesignSystemPage() {
  return (
    <main className="min-h-dvh bg-fond px-6 py-10">
      <div className="mx-auto max-w-5xl space-y-12">
        <header className="space-y-1">
          <p className="text-sm font-medium uppercase tracking-wide text-sarcelle">
            ChantierSync · Poste de pilotage
          </p>
          <h1 className="text-3xl font-bold text-marine">Système de design</h1>
          <p className="text-texte-secondaire">
            Charte graphique Schiavone appliquée en jetons réutilisables.
          </p>
        </header>

        <Section titre="Couleurs">
          <div className="space-y-6">
            <GroupeCouleurs titre="Marque" nuances={marque} />
            <GroupeCouleurs titre="Fonds et surfaces" nuances={fonds} />
            <GroupeCouleurs titre="Textes" nuances={textes} />
            <GroupeCouleurs titre="États" nuances={etats} />
          </div>
        </Section>

        <Section titre="Typographie">
          <div className="space-y-5 rounded-carte border border-bordure bg-surface p-6 shadow-douce">
            <div className="space-y-3">
              <p className="text-3xl font-bold">Titre 1 — supervision des opérations</p>
              <p className="text-xl font-semibold">Titre 2 — suivi de l'avancement</p>
              <p className="text-lg font-semibold">Titre 3 — corps d'état prioritaires</p>
              <p className="text-base font-normal">
                Corps — texte courant de l'interface, lisible et sobre, destiné à la lecture
                prolongée sur poste de bureau.
              </p>
              <p className="text-xs font-medium text-texte-secondaire">
                Mention — légende et information secondaire
              </p>
            </div>
            <div className="flex flex-wrap gap-6 border-t border-bordure pt-4">
              <span className="text-base font-normal">Régulier 400</span>
              <span className="text-base font-medium">Moyen 500</span>
              <span className="text-base font-semibold">Demi-gras 600</span>
              <span className="text-base font-bold">Gras 700</span>
            </div>
          </div>
        </Section>

        <Section titre="Rayons et élévation">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="rounded-carte border border-bordure bg-surface p-6 shadow-douce">
              <div className="mb-3 h-16 rounded-carte bg-fond-alt" />
              <p className="text-sm font-semibold">Carte</p>
              <p className="text-xs text-texte-secondaire">Rayon 16 px · ombre douce</p>
            </div>
            <div className="rounded-carte border border-bordure bg-surface p-6 shadow-douce">
              <div className="mb-3 h-16 rounded-controle bg-fond-alt" />
              <p className="text-sm font-semibold">Contrôle</p>
              <p className="text-xs text-texte-secondaire">Rayon 12 px · boutons, champs</p>
            </div>
            <div className="rounded-carte border border-bordure bg-surface p-6 shadow-levee">
              <div className="mb-3 h-16 rounded-full bg-fond-alt" />
              <p className="text-sm font-semibold">Pilule · survol</p>
              <p className="text-xs text-texte-secondaire">Plein arrondi · ombre levée</p>
            </div>
          </div>
        </Section>

        <Section titre="Pilules de statut">
          <div className="rounded-carte border border-bordure bg-surface p-6 shadow-douce">
            <div className="flex flex-wrap gap-3">
              {statuts.map((s) => {
                const Icone = s.icone
                return (
                  <span
                    key={s.libelle}
                    className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-sm font-medium ${s.pilule}`}
                  >
                    <Icone size={16} weight="regular" aria-hidden />
                    {s.libelle}
                  </span>
                )
              })}
            </div>
            <p className="mt-4 text-xs text-texte-secondaire">
              Un statut est toujours porté par une icône et un libellé, jamais par la couleur seule.
            </p>
          </div>
        </Section>

        <Section titre="Iconographie · Phosphor">
          <div className="rounded-carte border border-bordure bg-surface p-6 shadow-douce">
            <div className="grid grid-cols-3 gap-6 sm:grid-cols-4 lg:grid-cols-8">
              {icones.map((i) => {
                const Icone = i.composant
                return (
                  <div key={i.libelle} className="flex flex-col items-center gap-2 text-center">
                    <Icone size={28} weight="regular" className="text-marine" aria-hidden />
                    <span className="text-xs text-texte-secondaire">{i.libelle}</span>
                  </div>
                )
              })}
            </div>
          </div>
        </Section>
      </div>
    </main>
  )
}
