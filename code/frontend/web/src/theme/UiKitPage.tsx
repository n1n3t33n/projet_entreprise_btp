import {
  ArrowsClockwise,
  Buildings,
  CheckCircle,
  ClipboardText,
  DownloadSimple,
  FileArrowDown,
  Package,
  Plus,
  Printer,
  Stack,
  Trash,
  Users,
  Warehouse,
  Warning,
  WarningOctagon,
} from '@phosphor-icons/react'
import { useState, type ReactNode } from 'react'
import { PageListe } from '@/components/templates'
import {
  Button,
  Card,
  Drawer,
  FilterPill,
  FormField,
  Input,
  KpiCard,
  Modal,
  Select,
  StatusPill,
  Table,
  Tabs,
  Textarea,
  ThresholdGauge,
  ToastProvider,
  Tree,
  useToast,
  type ColonneTable,
  type NoeudArbre,
  type TonStatut,
} from '@/components/ui'
import { PARAMETRES_PAR_DEFAUT, resoudreSeuilConfort } from '@/config/parametres'
import { calculerNiveauSeuil, declencheAlerte, type NiveauSeuil } from '@/lib/seuils'

/*
  Données d'exemple.

  Elles vivent dans cette page et nulle part ailleurs : aucun composant de
  « components/ui » ne connaît un article, un magasin ou un chantier. C'est la
  condition pour que la même bibliothèque serve au module stock, au module
  avancement et à l'espace acquéreur.
*/

type ArticleExemple = {
  id: string
  reference: string
  designation: string
  magasin: string
  unite: string
  stock: number
  seuilMini: number
  seuilConfort: number | null
  capacite: number
  statut: { libelle: string; ton: TonStatut }
}

const articles: ArticleExemple[] = [
  {
    id: 'a-001',
    reference: 'CIM-42',
    designation: 'Ciment CPJ 42,5',
    magasin: 'Magasin central',
    unite: 'sac',
    stock: 18,
    seuilMini: 40,
    seuilConfort: 90,
    capacite: 200,
    statut: { libelle: 'À réapprovisionner', ton: 'alerte' },
  },
  {
    id: 'a-002',
    reference: 'FER-12',
    designation: 'Fer à béton Ø 12',
    magasin: 'Magasin central',
    unite: 'barre',
    stock: 310,
    seuilMini: 120,
    seuilConfort: 260,
    capacite: 400,
    statut: { libelle: 'Disponible', ton: 'succes' },
  },
  {
    id: 'a-003',
    reference: 'SAB-01',
    designation: 'Sable lavé 0/4',
    magasin: 'Aire de stockage',
    unite: 'm³',
    stock: 0,
    seuilMini: 15,
    seuilConfort: 35,
    capacite: 60,
    statut: { libelle: 'Rupture', ton: 'danger' },
  },
  {
    id: 'a-004',
    reference: 'PEI-05',
    designation: 'Peinture acrylique blanche',
    magasin: 'Magasin finitions',
    unite: 'pot',
    stock: 46,
    seuilMini: 20,
    seuilConfort: 45,
    capacite: 80,
    statut: { libelle: 'Disponible', ton: 'succes' },
  },
  {
    id: 'a-005',
    reference: 'CAR-60',
    designation: 'Carreaux grès 60 × 60',
    magasin: 'Magasin finitions',
    unite: 'boîte',
    stock: 0,
    seuilMini: 25,
    seuilConfort: null,
    capacite: 150,
    statut: { libelle: 'Rupture', ton: 'danger' },
  },
  {
    id: 'a-006',
    reference: 'TUB-110',
    designation: 'Tube PVC Ø 110',
    magasin: 'Magasin plomberie',
    unite: 'barre',
    stock: 52,
    seuilMini: 30,
    seuilConfort: 70,
    capacite: 120,
    statut: { libelle: 'Disponible', ton: 'succes' },
  },
  {
    id: 'a-007',
    reference: 'GRA-15',
    designation: 'Gravier 5/15',
    magasin: 'Aire de stockage',
    unite: 'm³',
    stock: 9,
    seuilMini: 20,
    seuilConfort: 45,
    capacite: 80,
    statut: { libelle: 'À réapprovisionner', ton: 'alerte' },
  },
  {
    id: 'a-008',
    reference: 'ENC-04',
    designation: 'Enduit de lissage',
    magasin: 'Magasin finitions',
    unite: 'sac',
    stock: 74,
    seuilMini: 25,
    seuilConfort: 55,
    capacite: 90,
    statut: { libelle: 'Disponible', ton: 'succes' },
  },
]

const colonnesArticles: ColonneTable<ArticleExemple>[] = [
  {
    cle: 'reference',
    entete: 'Référence',
    triable: true,
    valeurTri: (ligne) => ligne.reference,
    rendu: (ligne) => <span className="font-mono text-xs font-semibold">{ligne.reference}</span>,
    largeur: '8rem',
  },
  {
    cle: 'designation',
    entete: 'Désignation',
    triable: true,
    valeurTri: (ligne) => ligne.designation,
    rendu: (ligne) => <span className="font-medium">{ligne.designation}</span>,
  },
  {
    cle: 'magasin',
    entete: 'Magasin',
    triable: true,
    valeurTri: (ligne) => ligne.magasin,
    rendu: (ligne) => <span className="text-texte-secondaire">{ligne.magasin}</span>,
  },
  {
    cle: 'stock',
    entete: 'Stock',
    alignement: 'droite',
    triable: true,
    valeurTri: (ligne) => ligne.stock,
    rendu: (ligne) => (
      <span className="font-semibold">
        {ligne.stock} {ligne.unite}
      </span>
    ),
    largeur: '9rem',
  },
  {
    cle: 'seuil',
    entete: 'Niveau',
    rendu: (ligne) => (
      <ThresholdGauge
        valeur={ligne.stock}
        seuilMini={ligne.seuilMini}
        seuilConfort={resoudreSeuilConfort(ligne.seuilMini, ligne.seuilConfort)}
        capacite={ligne.capacite}
        unite={ligne.unite}
        afficherValeurs={false}
        taille="sm"
        className="w-36"
      />
    ),
    largeur: '11rem',
  },
  {
    cle: 'statut',
    entete: 'Statut',
    rendu: (ligne) => (
      <StatusPill libelle={ligne.statut.libelle} ton={ligne.statut.ton} taille="sm" />
    ),
    largeur: '12rem',
  },
]

const arborescenceMagasins: NoeudArbre[] = [
  {
    id: 'chantier-bassam',
    libelle: 'Chantier de Grand-Bassam',
    icone: Buildings,
    enfants: [
      {
        id: 'magasin-central',
        libelle: 'Magasin central',
        icone: Warehouse,
        badge: '2 familles',
        enfants: [
          { id: 'famille-gros-oeuvre', libelle: 'Gros œuvre', icone: Package, badge: 2 },
          { id: 'famille-ferraillage', libelle: 'Ferraillage', icone: Package, badge: 1 },
        ],
      },
      {
        id: 'magasin-finitions',
        libelle: 'Magasin finitions',
        icone: Warehouse,
        badge: '3 familles',
        enfants: [
          { id: 'famille-peinture', libelle: 'Peinture', icone: Package, badge: 1 },
          { id: 'famille-carrelage', libelle: 'Carrelage', icone: Package, badge: 1 },
          { id: 'famille-enduits', libelle: 'Enduits', icone: Package, badge: 1 },
        ],
      },
      {
        id: 'aire-stockage',
        libelle: 'Aire de stockage extérieure',
        icone: Warehouse,
        badge: '2 familles',
        enfants: [
          { id: 'famille-granulats', libelle: 'Granulats', icone: Package, badge: 2 },
          { id: 'famille-divers', libelle: 'Divers', icone: Package, desactive: true },
        ],
      },
    ],
  },
]

/*
  Niveaux déduits des seuils, exactement comme le fera le module stock : le
  seuil de confort vient du référentiel quand l'article le porte, sinon des
  paramètres de l'application. Aucun comptage n'est saisi à la main.
*/
const niveauxArticles = articles.map((article) =>
  calculerNiveauSeuil({
    valeur: article.stock,
    seuilMini: article.seuilMini,
    seuilConfort: resoudreSeuilConfort(article.seuilMini, article.seuilConfort),
  }),
)

const compterNiveau = (niveau: NiveauSeuil) =>
  niveauxArticles.filter((element) => element === niveau).length

const articlesEnAlerte = niveauxArticles.filter(declencheAlerte).length

const tonsStatut: { ton: TonStatut; libelle: string }[] = [
  { ton: 'neutre', libelle: 'À faire' },
  { ton: 'information', libelle: 'En cours' },
  { ton: 'succes', libelle: 'Terminée' },
  { ton: 'alerte', libelle: 'En retard' },
  { ton: 'danger', libelle: 'Bloquée' },
]

const casSeuil = [
  { titre: 'Stock confortable', valeur: 180, seuilMini: 40, seuilConfort: 90, capacite: 200 },
  { titre: 'Seuil d’alerte atteint', valeur: 70, seuilMini: 40, seuilConfort: 90, capacite: 200 },
  { titre: 'Sous le seuil d’alerte', valeur: 18, seuilMini: 40, seuilConfort: 90, capacite: 200 },
  { titre: 'Rupture', valeur: 0, seuilMini: 40, seuilConfort: 90, capacite: 200 },
]

function Section({
  titre,
  description,
  children,
}: {
  titre: string
  description?: string
  children: ReactNode
}) {
  return (
    <section className="space-y-4">
      <div className="space-y-1">
        <h2 className="text-xl font-bold text-marine">{titre}</h2>
        {description && <p className="text-sm text-texte-secondaire">{description}</p>}
      </div>
      {children}
    </section>
  )
}

function ContenuUiKit() {
  const { afficherToast } = useToast()

  const [filtresActifs, setFiltresActifs] = useState<string[]>(['sous-seuil'])
  const [filtresRetires, setFiltresRetires] = useState<string[]>([])
  const [ongletActif, setOngletActif] = useState('articles')
  const [tiroirOuvert, setTiroirOuvert] = useState(false)
  const [modaleOuverte, setModaleOuverte] = useState(false)
  const [noeudSelectionne, setNoeudSelectionne] = useState('magasin-finitions')
  const [designation, setDesignation] = useState('')
  const [lignesRetenues, setLignesRetenues] = useState<string[]>([])

  function basculerFiltre(cle: string) {
    setFiltresActifs((liste) =>
      liste.includes(cle) ? liste.filter((element) => element !== cle) : [...liste, cle],
    )
  }

  const filtresDisponibles = [
    { cle: 'sous-seuil', libelle: 'Niveau', valeur: 'sous le seuil' },
    { cle: 'magasin', libelle: 'Magasin', valeur: 'finitions' },
    { cle: 'corps-etat', libelle: "Corps d'état", valeur: 'second œuvre' },
  ].filter((filtre) => !filtresRetires.includes(filtre.cle))

  return (
    <main className="min-h-dvh bg-fond px-6 py-10">
      <div className="mx-auto max-w-6xl space-y-12">
        <header className="space-y-1">
          <p className="text-sm font-medium uppercase tracking-wide text-sarcelle">
            ChantierSync · Poste de pilotage
          </p>
          <h1 className="text-3xl font-bold text-marine">Bibliothèque de composants</h1>
          <p className="max-w-3xl text-texte-secondaire">
            Composants d'interface réutilisables du poste de pilotage. Chaque composant est piloté
            par la charte graphique et ne reçoit ses contenus que par ses propriétés. Les données
            affichées sur cette page sont des exemples locaux, destinés à la seule démonstration.
          </p>
        </header>

        <Section
          titre="Boutons"
          description="Un seul bouton primaire par zone d'écran. L'icône reste décorative : le libellé porte le sens de l'action."
        >
          <Card>
            <div className="space-y-5">
              <div className="flex flex-wrap items-center gap-3">
                <Button variante="primaire" icone={Plus}>
                  Nouvelle fiche de route
                </Button>
                <Button variante="secondaire" icone={DownloadSimple}>
                  Exporter
                </Button>
                <Button variante="discret" icone={Printer}>
                  Imprimer
                </Button>
                <Button variante="danger" icone={Trash}>
                  Supprimer
                </Button>
              </div>

              <div className="flex flex-wrap items-center gap-3 border-t border-bordure pt-5">
                <Button variante="primaire" taille="sm">
                  Petit
                </Button>
                <Button variante="primaire" taille="md">
                  Moyen
                </Button>
                <Button variante="primaire" taille="lg">
                  Grand
                </Button>
              </div>

              <div className="flex flex-wrap items-center gap-3 border-t border-bordure pt-5">
                <Button variante="primaire" enChargement>
                  Synchronisation
                </Button>
                <Button variante="secondaire" disabled>
                  Indisponible
                </Button>
                <Button
                  variante="secondaire"
                  icone={ArrowsClockwise}
                  aria-label="Relancer la synchronisation"
                />
              </div>
            </div>
          </Card>
        </Section>

        <Section
          titre="Indicateurs"
          description="La couleur d'une variation dépend du sens souhaité, pas du signe : une hausse des retards est défavorable."
        >
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <KpiCard
              libelle="Avancement global"
              valeur="62"
              unite="%"
              icone={ClipboardText}
              accent="marine"
              variation={4.1}
              variationLibelle="vs semaine passée"
            />
            <KpiCard
              libelle="Fiches en retard"
              valeur="7"
              icone={WarningOctagon}
              accent="danger"
              variation={12.5}
              variationLibelle="vs semaine passée"
              tendanceSouhaitee="baisse"
            />
            <KpiCard
              libelle="Articles sous le seuil"
              valeur="3"
              icone={Package}
              accent="or"
              variation={-25}
              variationLibelle="vs semaine passée"
              tendanceSouhaitee="baisse"
            />
            <KpiCard
              libelle="Comptes actifs"
              valeur="—"
              icone={Users}
              accent="sarcelle"
              chargement
            />
          </div>
        </Section>

        <Section
          titre="Statuts"
          description="Un statut associe toujours une icône et un libellé : la couleur ne porte jamais seule l'information."
        >
          <Card>
            <div className="flex flex-wrap gap-3">
              {tonsStatut.map((element) => (
                <StatusPill key={element.ton} libelle={element.libelle} ton={element.ton} />
              ))}
            </div>
          </Card>
        </Section>

        <Section
          titre="Jauges de seuil"
          description="Quatre niveaux : plein tant que le stock reste confortable, mini dès que le seuil d'alerte est atteint, critique en dessous, vide à l'épuisement. Les rappels se déclenchent à partir du niveau mini et se resserrent à mesure que le stock descend."
        >
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {casSeuil.map((cas) => (
              <Card key={cas.titre} titre={cas.titre} niveauTitre={3}>
                <ThresholdGauge
                  valeur={cas.valeur}
                  seuilMini={cas.seuilMini}
                  seuilConfort={cas.seuilConfort}
                  capacite={cas.capacite}
                  unite="sac"
                />
              </Card>
            ))}
          </div>
        </Section>

        <Section
          titre="Filtres"
          description="Les pilules de filtre se cumulent. Chacune peut être basculée, et retirée quand le critère n'est plus pertinent."
        >
          <Card>
            <div className="flex flex-wrap items-center gap-2">
              {filtresDisponibles.map((filtre) => (
                <FilterPill
                  key={filtre.cle}
                  libelle={filtre.libelle}
                  valeur={filtre.valeur}
                  actif={filtresActifs.includes(filtre.cle)}
                  onBasculer={() => basculerFiltre(filtre.cle)}
                  onRetirer={() => setFiltresRetires((liste) => [...liste, filtre.cle])}
                />
              ))}
              {filtresRetires.length > 0 && (
                <Button variante="discret" taille="sm" onClick={() => setFiltresRetires([])}>
                  Rétablir les filtres retirés
                </Button>
              )}
            </div>
          </Card>
        </Section>

        <Section
          titre="Onglets"
          description="Un seul arrêt de tabulation : la touche Tab entre dans la série, les flèches gauche et droite changent d'onglet."
        >
          <Card>
            <Tabs
              intitule="Vues du magasin"
              onglets={[
                { id: 'articles', libelle: 'Articles', icone: Package, badge: articles.length },
                { id: 'mouvements', libelle: 'Mouvements', icone: ArrowsClockwise },
                { id: 'familles', libelle: 'Familles', icone: Stack },
                { id: 'inventaire', libelle: 'Inventaire', icone: ClipboardText, desactive: true },
              ]}
              actif={ongletActif}
              onChanger={setOngletActif}
            >
              <p className="text-sm text-texte-secondaire">
                Contenu de l'onglet « {ongletActif} ». Le panneau est remonté à chaque changement,
                ce qui rejoue son animation d'entrée.
              </p>
            </Tabs>
          </Card>
        </Section>

        <Section
          titre="Champs de formulaire"
          description="Libellé toujours visible, aide sous le champ, erreur annoncée à côté du champ concerné. Le mode lecture seule laisse la valeur sélectionnable et copiable."
        >
          <Card>
            <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
              <FormField
                libelle="Désignation de l'article"
                aide="Nom tel qu'il figure sur le bon de livraison."
                requis
              >
                {(champ) => (
                  <Input
                    {...champ}
                    value={designation}
                    onChange={(evenement) => setDesignation(evenement.target.value)}
                    placeholder="Ciment CPJ 42,5"
                  />
                )}
              </FormField>

              <FormField
                libelle="Seuil minimum"
                erreur="Le seuil doit être un nombre positif."
                requis
              >
                {(champ) => <Input {...champ} type="number" defaultValue={-5} invalide />}
              </FormField>

              <FormField libelle="Magasin de rattachement" requis>
                {(champ) => (
                  <Select {...champ} defaultValue="central">
                    <option value="central">Magasin central</option>
                    <option value="finitions">Magasin finitions</option>
                    <option value="aire">Aire de stockage extérieure</option>
                  </Select>
                )}
              </FormField>

              <FormField
                libelle="Référence interne"
                aide="Attribuée automatiquement, non modifiable."
              >
                {(champ) => <Input {...champ} value="CIM-42" lectureSeule />}
              </FormField>

              <FormField
                libelle="Observation du magasinier"
                aide="Visible par le responsable technique."
                className="md:col-span-2"
              >
                {(champ) => (
                  <Textarea {...champ} placeholder="Palette reçue partiellement humide…" />
                )}
              </FormField>
            </div>
          </Card>
        </Section>

        <Section
          titre="Tableau"
          description="En-tête collant, tri sur trois états, sélection multiple avec barre d'actions groupées, pagination et défilement horizontal."
        >
          <Table
            intitule="Articles en stock du chantier de Grand-Bassam"
            colonnes={colonnesArticles}
            lignes={articles}
            cleLigne={(ligne) => ligne.id}
            triInitial={{ cle: 'reference', sens: 'asc' }}
            selectionnable
            parPage={5}
            hauteurMax="26rem"
            onSelectionChanger={setLignesRetenues}
            actionsGroupees={(lignesSelectionnees, reinitialiser) => (
              <>
                <Button
                  variante="secondaire"
                  taille="sm"
                  icone={FileArrowDown}
                  onClick={() => {
                    afficherToast({
                      titre: 'Export préparé',
                      message: `${lignesSelectionnees.length} article(s) ajoutés au bon de commande.`,
                      ton: 'succes',
                    })
                    reinitialiser()
                  }}
                >
                  Préparer un bon de commande
                </Button>
                <Button
                  variante="secondaire"
                  taille="sm"
                  icone={ArrowsClockwise}
                  onClick={() => {
                    afficherToast({
                      titre: 'Réapprovisionnement demandé',
                      message: `Demande transmise pour ${lignesSelectionnees.length} article(s).`,
                      ton: 'information',
                    })
                    reinitialiser()
                  }}
                >
                  Demander un réapprovisionnement
                </Button>
              </>
            )}
          />
          <p className="text-xs text-texte-secondaire">
            Sélection courante transmise au composant parent :{' '}
            {lignesRetenues.length === 0 ? 'aucune ligne' : lignesRetenues.join(', ')}
          </p>
        </Section>

        <Section
          titre="Panneaux superposés"
          description="Tiroir et modale sont rendus par un portail, confinent le focus clavier, se referment avec la touche Échap et rendent le focus au bouton qui les a ouverts."
        >
          <Card>
            <div className="flex flex-wrap gap-3">
              <Button variante="primaire" onClick={() => setTiroirOuvert(true)}>
                Ouvrir le tiroir
              </Button>
              <Button variante="danger" onClick={() => setModaleOuverte(true)}>
                Ouvrir la modale de confirmation
              </Button>
            </div>
          </Card>

          <Drawer
            ouvert={tiroirOuvert}
            onFermer={() => setTiroirOuvert(false)}
            titre="Ciment CPJ 42,5"
            description="Magasin central · référence CIM-42"
            pied={
              <>
                <Button variante="secondaire" onClick={() => setTiroirOuvert(false)}>
                  Annuler
                </Button>
                <Button
                  variante="primaire"
                  icone={CheckCircle}
                  onClick={() => {
                    setTiroirOuvert(false)
                    afficherToast({ titre: 'Fiche article enregistrée', ton: 'succes' })
                  }}
                >
                  Enregistrer
                </Button>
              </>
            }
          >
            <div className="space-y-5">
              <ThresholdGauge
                valeur={18}
                seuilMini={40}
                seuilConfort={90}
                capacite={200}
                unite="sac"
              />
              <FormField libelle="Seuil minimum" aide="Déclenche l'alerte de réapprovisionnement.">
                {(champ) => <Input {...champ} type="number" defaultValue={40} />}
              </FormField>
              <FormField libelle="Observation">
                {(champ) => <Textarea {...champ} rows={3} />}
              </FormField>
            </div>
          </Drawer>

          <Modal
            ouvert={modaleOuverte}
            onFermer={() => setModaleOuverte(false)}
            titre="Supprimer la fiche de route ?"
            description="Cette action retire la fiche et les pointages associés."
            ton="danger"
            taille="sm"
            actions={
              <>
                <Button variante="secondaire" onClick={() => setModaleOuverte(false)}>
                  Annuler
                </Button>
                <Button
                  variante="danger"
                  icone={Trash}
                  onClick={() => {
                    setModaleOuverte(false)
                    afficherToast({
                      titre: 'Fiche de route supprimée',
                      message: 'Les pointages associés ont été retirés.',
                      ton: 'danger',
                    })
                  }}
                >
                  Supprimer
                </Button>
              </>
            }
          >
            <p className="text-sm text-texte-secondaire">
              La suppression est définitive. Les techniciens ayant déjà coché des tâches de cette
              fiche en perdront la trace.
            </p>
          </Modal>
        </Section>

        <Section
          titre="Notifications"
          description="Une confirmation attend la fin de la phrase en cours de lecture, une erreur interrompt : les deux n'emploient pas le même rôle d'annonce."
        >
          <Card>
            <div className="flex flex-wrap gap-3">
              <Button
                variante="secondaire"
                onClick={() => afficherToast({ titre: 'Synchronisation terminée', ton: 'succes' })}
              >
                Succès
              </Button>
              <Button
                variante="secondaire"
                onClick={() =>
                  afficherToast({
                    titre: 'Mode hors-ligne',
                    message: 'Les pointages seront transmis au retour du réseau.',
                    ton: 'information',
                  })
                }
              >
                Information
              </Button>
              <Button
                variante="secondaire"
                onClick={() =>
                  afficherToast({
                    titre: 'Trois articles sous le seuil mini',
                    ton: 'alerte',
                  })
                }
              >
                Alerte
              </Button>
              <Button
                variante="secondaire"
                onClick={() =>
                  afficherToast({
                    titre: 'Échec de la synchronisation',
                    message: 'Le serveur est injoignable. Nouvelle tentative dans 5 minutes.',
                    ton: 'danger',
                    dureeMs: 0,
                  })
                }
              >
                Erreur persistante
              </Button>
            </div>
          </Card>
        </Section>

        <Section
          titre="Arbre"
          description="Navigation au clavier complète : flèches haut et bas pour parcourir, droite et gauche pour déplier et replier, Entrée pour sélectionner."
        >
          <Card>
            <Tree
              intitule="Magasins et familles d'articles"
              noeuds={arborescenceMagasins}
              selectionne={noeudSelectionne}
              onSelectionner={setNoeudSelectionne}
              ouvertsInitiaux={['chantier-bassam', 'magasin-central']}
              className="max-w-md"
            />
          </Card>
        </Section>

        <Section
          titre="Gabarit de page"
          description="Premier gabarit partagé : en-tête, indicateurs, filtres puis contenu, avec entrée en cascade. Le même gabarit sert un rôle consultant en retirant ses actions d'écriture."
        >
          <div className="rounded-carte border border-dashed border-bordure bg-surface p-6">
            <PageListe
              titre="Stock du chantier de Grand-Bassam"
              description="Niveaux par article et par magasin, mis à jour à chaque synchronisation."
              etiquette={<StatusPill libelle="Synchronisé" ton="succes" taille="sm" />}
              actions={
                <>
                  <Button variante="secondaire" icone={DownloadSimple}>
                    Exporter
                  </Button>
                  <Button variante="primaire" icone={Plus}>
                    Entrée de stock
                  </Button>
                </>
              }
              indicateurs={
                <>
                  <KpiCard libelle="Références suivies" valeur={articles.length} icone={Package} />
                  <KpiCard
                    libelle="En alerte"
                    valeur={articlesEnAlerte}
                    icone={Warning}
                    accent="or"
                    tendanceSouhaitee="baisse"
                    variation={-16.7}
                  />
                  <KpiCard
                    libelle="Sous le seuil d'alerte"
                    valeur={compterNiveau('critique')}
                    icone={WarningOctagon}
                    accent="or"
                  />
                  <KpiCard
                    libelle="En rupture"
                    valeur={compterNiveau('vide')}
                    icone={WarningOctagon}
                    accent="danger"
                  />
                </>
              }
              filtres={
                <>
                  <FilterPill libelle="Magasin" valeur="tous" actif onBasculer={() => undefined} />
                  <FilterPill
                    libelle="Niveau"
                    valeur="sous le seuil"
                    onBasculer={() => undefined}
                  />
                </>
              }
            >
              <Table
                intitule="Extrait du stock, dans le gabarit de page"
                colonnes={colonnesArticles.slice(0, 4)}
                lignes={articles.slice(0, 4)}
                cleLigne={(ligne) => ligne.id}
              />
            </PageListe>
          </div>
        </Section>
      </div>
    </main>
  )
}

export function UiKitPage() {
  return (
    <ToastProvider dureeParDefautMs={PARAMETRES_PAR_DEFAUT.notifications.dureeToastMs}>
      <ContenuUiKit />
    </ToastProvider>
  )
}
