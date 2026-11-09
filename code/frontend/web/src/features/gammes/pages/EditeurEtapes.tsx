/*
  Éditeur des étapes-modèles d'une gamme en brouillon (EF-REF-05).

  N'est ouvert que pour une gamme BROUILLON : une gamme publiée est un contrat
  figé. L'éditeur montre en permanence le poids total, car c'est lui qui sert de
  dénominateur au calcul d'avancement (RG-A6) ; rien n'impose un total de 100,
  mais l'afficher évite les gammes déséquilibrées par inadvertance.
*/

import { useEffect, useState } from 'react'
import { Plus, Trash } from '@phosphor-icons/react'
import { Button, Drawer, Input, Select, useToast } from '@/components/ui'
import { enregistrerEtapes } from '@/features/gammes/api'
import { formatPourcentage } from '@/lib/format'
import type { CorpsEtat, EtapeModele, SaisieEtapeModele } from '@/features/gammes/types'

export type EditeurEtapesProps = {
  ouvert: boolean
  onFermer: () => void
  idGamme: string
  libelleGamme: string
  etapesInitiales: EtapeModele[]
  corpsEtat: CorpsEtat[]
  onEnregistre: () => void
}

type LigneEdition = {
  cleLocale: string
  id: string
  code: string
  libelle: string
  poids: string
  controleRequis: boolean
  codeCorpsEtat: string
}

let compteurLocal = 0

function ligneVierge(corpsParDefaut: string): LigneEdition {
  compteurLocal += 1
  return {
    cleLocale: `n-${compteurLocal}`,
    id: '',
    code: '',
    libelle: '',
    poids: '0',
    controleRequis: false,
    codeCorpsEtat: corpsParDefaut,
  }
}

export function EditeurEtapes({
  ouvert,
  onFermer,
  idGamme,
  libelleGamme,
  etapesInitiales,
  corpsEtat,
  onEnregistre,
}: EditeurEtapesProps) {
  const { afficherToast } = useToast()
  const [lignes, setLignes] = useState<LigneEdition[]>([])
  const [enCours, setEnCours] = useState(false)

  useEffect(() => {
    if (!ouvert) return
    setLignes(
      etapesInitiales.map((etape, index) => ({
        cleLocale: `e-${etape.id}-${index}`,
        id: etape.id,
        code: etape.code,
        libelle: etape.libelle,
        poids: String(etape.poids),
        controleRequis: etape.controleRequis,
        codeCorpsEtat: etape.codeCorpsEtat,
      })),
    )
  }, [ouvert, etapesInitiales])

  const corpsParDefaut = corpsEtat[0]?.code ?? ''
  const poidsTotal = lignes.reduce((somme, ligne) => somme + (Number(ligne.poids) || 0), 0)

  function modifier(cle: string, champ: keyof LigneEdition, valeur: string | boolean) {
    setLignes((precedentes) =>
      precedentes.map((ligne) => (ligne.cleLocale === cle ? { ...ligne, [champ]: valeur } : ligne)),
    )
  }

  function ajouter() {
    setLignes((precedentes) => [...precedentes, ligneVierge(corpsParDefaut)])
  }

  function retirer(cle: string) {
    setLignes((precedentes) => precedentes.filter((ligne) => ligne.cleLocale !== cle))
  }

  async function enregistrer() {
    const valides = lignes.filter((ligne) => ligne.libelle.trim() !== '')
    if (valides.length === 0) {
      afficherToast({
        ton: 'danger',
        titre: 'Gamme vide',
        message: 'Ajouter au moins une étape avant d’enregistrer.',
      })
      return
    }

    const saisies: SaisieEtapeModele[] = valides.map((ligne, index) => ({
      id: ligne.id,
      code: ligne.code.trim() || `EM-${index + 1}`,
      libelle: ligne.libelle.trim(),
      ordre: index + 1,
      poids: Number(ligne.poids) || 0,
      controleRequis: ligne.controleRequis,
      codeCorpsEtat: ligne.codeCorpsEtat,
    }))

    setEnCours(true)
    try {
      await enregistrerEtapes(idGamme, saisies)
      afficherToast({
        ton: 'succes',
        titre: 'Étapes enregistrées',
        message: `${saisies.length} étape${saisies.length > 1 ? 's' : ''} · poids total ${poidsTotal}`,
      })
      onFermer()
      onEnregistre()
    } catch (erreur) {
      afficherToast({
        ton: 'danger',
        titre: "Les étapes n'ont pas pu être enregistrées",
        message: erreur instanceof Error ? erreur.message : undefined,
      })
    } finally {
      setEnCours(false)
    }
  }

  return (
    <Drawer
      ouvert={ouvert}
      onFermer={onFermer}
      titre="Modifier les étapes"
      description={libelleGamme}
      largeur="lg"
      pied={
        <div className="flex items-center justify-between gap-4">
          <span className="text-sm text-texte-secondaire">
            Poids total :{' '}
            <span className="font-semibold text-texte">{formatPourcentage(poidsTotal)}</span>
          </span>
          <div className="flex gap-2">
            <Button variante="secondaire" onClick={onFermer} disabled={enCours}>
              Annuler
            </Button>
            <Button variante="primaire" onClick={enregistrer} enChargement={enCours}>
              Enregistrer les étapes
            </Button>
          </div>
        </div>
      }
    >
      <div className="flex flex-col gap-3">
        {lignes.map((ligne, index) => (
          <div
            key={ligne.cleLocale}
            className="flex flex-col gap-2 rounded-lg border border-bordure bg-fond-alt/40 p-3"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-texte-secondaire">Étape {index + 1}</span>
              <Button
                variante="discret"
                taille="sm"
                icone={Trash}
                aria-label={`Retirer l'étape ${index + 1}`}
                onClick={() => retirer(ligne.cleLocale)}
              />
            </div>
            <Input
              value={ligne.libelle}
              onChange={(evenement) => modifier(ligne.cleLocale, 'libelle', evenement.target.value)}
              placeholder="Libellé de l'étape"
            />
            <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
              <Select
                value={ligne.codeCorpsEtat}
                aria-label="Corps d'état"
                onChange={(evenement) =>
                  modifier(ligne.cleLocale, 'codeCorpsEtat', evenement.target.value)
                }
              >
                {corpsEtat.map((corps) => (
                  <option key={corps.code} value={corps.code}>
                    {corps.libelle}
                  </option>
                ))}
              </Select>
              <Input
                type="number"
                min={0}
                step="0.1"
                value={ligne.poids}
                aria-label="Poids"
                onChange={(evenement) => modifier(ligne.cleLocale, 'poids', evenement.target.value)}
                placeholder="Poids"
              />
              <label className="flex items-center gap-2 text-sm text-texte">
                <input
                  type="checkbox"
                  checked={ligne.controleRequis}
                  onChange={(evenement) =>
                    modifier(ligne.cleLocale, 'controleRequis', evenement.target.checked)
                  }
                  className="h-4 w-4 rounded border-bordure"
                />
                Contrôle requis
              </label>
            </div>
          </div>
        ))}

        <Button variante="secondaire" icone={Plus} onClick={ajouter}>
          Ajouter une étape
        </Button>
      </div>
    </Drawer>
  )
}
