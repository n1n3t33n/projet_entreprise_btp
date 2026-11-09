/*
  Import CSV des référentiels (EF-ADM-02 ; UC-4 « Importer les données initiales
  en CSV », acteur Administrateur). Charte § 9.2, écran 14.

  L'import se fait en deux temps, pour qu'une erreur de fichier ne touche jamais
  les données :
  1. ANALYSER : le serveur valide le contenu ligne par ligne et renvoie un
     rapport (lignes valides, lignes en erreur avec leur motif). Rien n'est
     écrit.
  2. IMPORTER : après avoir vu le rapport, l'administrateur confirme ; seules
     les lignes valides sont importées, et l'action est journalisée (EF-AUT-08).

  La MODIFICATION (l'import, qui écrit en masse) est réservée au rôle système,
  comme la matrice des droits et la révocation : un rôle à qui l'on ouvrirait
  l'écran en lecture voit le formulaire désactivé.
*/

import { useMemo, useState } from 'react'
import { FileArrowUp, MagnifyingGlass } from '@phosphor-icons/react'
import { Button, Card, type ColonneTable, FormField, Select, StatusPill, Table, Textarea, useToast } from '@/components/ui'
import { analyserImport, confirmerImport } from '@/features/admin/api/import-csv'
import type { CibleImport, LigneImport, RapportImport } from '@/features/admin/types/import-csv'

export type ImportReferentielsProps = {
  /** Autorise l'analyse et l'import. Réservé au rôle système. */
  peutImporter: boolean
}

const LIBELLE_CIBLE: Record<CibleImport, string> = {
  articles: 'Catalogue des articles',
  magasins: 'Magasins',
  chantiers: 'Chantiers et zones',
}

export function ImportReferentiels({ peutImporter }: ImportReferentielsProps) {
  const { afficherToast } = useToast()

  const [cible, setCible] = useState<CibleImport>('articles')
  const [contenu, setContenu] = useState('')
  const [rapport, setRapport] = useState<RapportImport | null>(null)
  const [analyseEnCours, setAnalyseEnCours] = useState(false)
  const [importEnCours, setImportEnCours] = useState(false)

  const peutAnalyser = peutImporter && contenu.trim() !== ''
  const peutConfirmer =
    peutImporter && rapport !== null && rapport.cible === cible && rapport.nombreValides > 0

  // Changer de cible ou de contenu invalide le rapport : il ne décrit plus ce
  // qui est à l'écran.
  function changerCible(valeur: CibleImport) {
    setCible(valeur)
    setRapport(null)
  }

  function changerContenu(valeur: string) {
    setContenu(valeur)
    setRapport(null)
  }

  async function analyser() {
    setAnalyseEnCours(true)
    try {
      setRapport(await analyserImport(cible, contenu))
    } catch (erreur) {
      afficherToast({
        ton: 'danger',
        titre: "L'analyse a échoué",
        message: erreur instanceof Error ? erreur.message : undefined,
      })
    } finally {
      setAnalyseEnCours(false)
    }
  }

  async function importer() {
    setImportEnCours(true)
    try {
      const resultat = await confirmerImport(cible, contenu)
      afficherToast({
        ton: 'succes',
        titre: 'Import effectué',
        message: `${resultat.nombreImportees} ligne(s) importée(s) dans « ${LIBELLE_CIBLE[cible]} ».`,
      })
      setContenu('')
      setRapport(null)
    } catch (erreur) {
      afficherToast({
        ton: 'danger',
        titre: "L'import a échoué",
        message: erreur instanceof Error ? erreur.message : undefined,
      })
    } finally {
      setImportEnCours(false)
    }
  }

  const colonnes: ColonneTable<LigneImport>[] = useMemo(() => {
    if (!rapport) {
      return []
    }
    const colonnesDonnees = rapport.colonnes.map<ColonneTable<LigneImport>>((nom, index) => ({
      cle: `col-${index}`,
      entete: nom,
      rendu: (ligne) => (
        <span className="text-sm text-texte">{ligne.valeurs[index] ?? ''}</span>
      ),
    }))
    return [
      {
        cle: 'numero',
        entete: 'Ligne',
        largeur: '5rem',
        rendu: (ligne) => <span className="text-xs text-texte-secondaire">{ligne.numero}</span>,
      },
      ...colonnesDonnees,
      {
        cle: 'etat',
        entete: 'État',
        largeur: '16rem',
        rendu: (ligne) =>
          ligne.erreur ? (
            <StatusPill ton="danger" taille="sm" libelle={ligne.erreur} />
          ) : (
            <StatusPill ton="succes" taille="sm" libelle="Valide" />
          ),
      },
    ]
  }, [rapport])

  return (
    <Card
      titre="Import CSV des référentiels"
      description="Charger en une fois les données initiales d'un référentiel, après contrôle ligne par ligne"
      actions={peutImporter ? undefined : <StatusPill ton="neutre" taille="sm" libelle="Lecture seule" />}
    >
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[18rem,1fr]">
        <div className="flex flex-col gap-4">
          <FormField libelle="Référentiel à importer">
            {(champ) => (
              <Select
                {...champ}
                value={cible}
                disabled={!peutImporter}
                onChange={(evenement) => changerCible(evenement.target.value as CibleImport)}
              >
                {(Object.keys(LIBELLE_CIBLE) as CibleImport[]).map((valeur) => (
                  <option key={valeur} value={valeur}>
                    {LIBELLE_CIBLE[valeur]}
                  </option>
                ))}
              </Select>
            )}
          </FormField>

          <div className="flex flex-col gap-2">
            <Button
              variante="secondaire"
              icone={MagnifyingGlass}
              onClick={analyser}
              disabled={!peutAnalyser}
              enChargement={analyseEnCours}
              pleineLargeur
            >
              Analyser le fichier
            </Button>
            <Button
              variante="primaire"
              icone={FileArrowUp}
              onClick={importer}
              disabled={!peutConfirmer}
              enChargement={importEnCours}
              pleineLargeur
            >
              {rapport && rapport.nombreValides > 0
                ? `Importer ${rapport.nombreValides} ligne(s)`
                : 'Importer'}
            </Button>
          </div>
        </div>

        <FormField
          libelle="Contenu CSV"
          aide="Première ligne = en-tête (ignorée). Séparateur « ; » ou « , ». Une ligne par enregistrement."
        >
          {(champ) => (
            <Textarea
              {...champ}
              value={contenu}
              disabled={!peutImporter}
              onChange={(evenement) => changerContenu(evenement.target.value)}
              rows={10}
              placeholder={'code;libelle;unite;seuil_minimal;seuil_critique\nCIM-01;Ciment CPA 42.5;sac;50;20'}
              className="font-mono text-xs"
            />
          )}
        </FormField>
      </div>

      {rapport && (
        <div className="mt-6 flex flex-col gap-3">
          <div className="flex flex-wrap items-center gap-2">
            <StatusPill ton="succes" libelle={`${rapport.nombreValides} ligne(s) valide(s)`} />
            {rapport.nombreErreurs > 0 && (
              <StatusPill ton="danger" libelle={`${rapport.nombreErreurs} ligne(s) en erreur`} />
            )}
            {rapport.nombreErreurs > 0 && (
              <span className="text-xs text-texte-secondaire">
                Les lignes en erreur ne seront pas importées.
              </span>
            )}
          </div>

          <Table
            intitule="Aperçu de l'import"
            colonnes={colonnes}
            lignes={rapport.lignes}
            cleLigne={(ligne) => String(ligne.numero)}
            parPage={10}
            messageVide="Aucune ligne de données dans le fichier."
            lectureSeule
          />
        </div>
      )}
    </Card>
  )
}
