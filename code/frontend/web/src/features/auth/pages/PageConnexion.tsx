/*
  Écran de connexion du poste de pilotage (charte § 9.2, écran 1 ;
  EF-AUT-04 : identifiant et mot de passe, verrouillage temporaire après
  échecs répétés).

  Formulaire contrôlé, validation en ligne, message d'échec distinct selon le
  motif renvoyé par le serveur. Pendant un verrouillage, le formulaire reste
  visible mais la soumission est refusée, avec le temps d'attente restant.
*/

import { useEffect, useState, type FormEvent } from 'react'
import { Navigate } from 'react-router-dom'
import { LockKey, SignIn, Warning } from '@phosphor-icons/react'
import { Button, FormField, Input } from '@/components/ui'
import { Logo } from '@/components/ui/Logo'
import { useSession } from '@/app/session-context'
import { ErreurConnexion, seConnecter } from '@/features/auth/api'
import { COMPTES_DEMONSTRATION } from '@/features/auth/presentation/demonstration'
import type { EchecConnexion } from '@/features/auth/types/domaine'

export function PageConnexion() {
  const { connecte, ouvrirSession } = useSession()

  const [identifiant, setIdentifiant] = useState('')
  const [motDePasse, setMotDePasse] = useState('')
  const [erreurs, setErreurs] = useState<{ identifiant?: string; motDePasse?: string }>({})
  const [echec, setEchec] = useState<EchecConnexion | null>(null)
  const [attente, setAttente] = useState(0)
  const [enCours, setEnCours] = useState(false)

  // Décompte du verrouillage temporaire : l'utilisateur voit le temps restant
  // au lieu d'un refus opaque.
  useEffect(() => {
    if (attente <= 0) {
      return
    }
    const minuterie = window.setTimeout(() => setAttente((valeur) => valeur - 1), 1000)
    return () => window.clearTimeout(minuterie)
  }, [attente])

  if (connecte) {
    return <Navigate to="/" replace />
  }

  async function soumettre(evenement: FormEvent) {
    evenement.preventDefault()

    const prochaines: typeof erreurs = {}
    if (identifiant.trim() === '') {
      prochaines.identifiant = 'Saisir un identifiant.'
    }
    if (motDePasse === '') {
      prochaines.motDePasse = 'Saisir un mot de passe.'
    }
    setErreurs(prochaines)
    if (Object.keys(prochaines).length > 0 || attente > 0) {
      return
    }

    setEnCours(true)
    setEchec(null)
    try {
      const session = await seConnecter({ identifiant: identifiant.trim(), motDePasse })
      ouvrirSession(session)
    } catch (erreur) {
      if (erreur instanceof ErreurConnexion) {
        setEchec(erreur.echec)
        setAttente(erreur.echec.secondesRestantes ?? 0)
      } else {
        setEchec({ motif: 'identifiants', message: 'La connexion a échoué.' })
      }
      setMotDePasse('')
    } finally {
      setEnCours(false)
    }
  }

  const bloque = attente > 0

  return (
    <main className="flex min-h-dvh items-center justify-center bg-fond px-4 py-10">
      <div className="w-full max-w-md">
        <div className="mb-6 flex justify-center">
          <Logo />
        </div>

        <section className="rounded-carte border border-bordure bg-surface p-6 shadow-douce">
          <h1 className="text-xl font-bold text-marine">Connexion</h1>
          <p className="mt-1 text-sm text-texte-secondaire">
            Poste de pilotage ChantierSync — accès réservé aux comptes nominatifs.
          </p>

          {echec && (
            <p
              role="alert"
              className="mt-4 flex items-start gap-2 rounded-controle border border-danger/30 bg-danger/5 px-3 py-2 text-sm font-medium text-danger"
            >
              {bloque ? (
                <LockKey size={16} weight="regular" aria-hidden className="mt-0.5 shrink-0" />
              ) : (
                <Warning size={16} weight="regular" aria-hidden className="mt-0.5 shrink-0" />
              )}
              <span>
                {echec.message}
                {bloque && ` Réessayez dans ${attente} seconde${attente > 1 ? 's' : ''}.`}
              </span>
            </p>
          )}

          <form onSubmit={soumettre} className="mt-5 flex flex-col gap-4" noValidate>
            <FormField libelle="Identifiant" requis erreur={erreurs.identifiant}>
              {(champ) => (
                <Input
                  {...champ}
                  autoComplete="username"
                  autoFocus
                  invalide={Boolean(erreurs.identifiant)}
                  value={identifiant}
                  onChange={(evenement) => {
                    setIdentifiant(evenement.target.value)
                    // Le verrouillage porte sur UN compte (EF-AUT-04) : changer
                    // d'identifiant doit rouvrir le formulaire, sinon un compte
                    // bloqué empêcherait tous les autres de se connecter.
                    setAttente(0)
                    setEchec(null)
                  }}
                />
              )}
            </FormField>

            <FormField libelle="Mot de passe" requis erreur={erreurs.motDePasse}>
              {(champ) => (
                <Input
                  {...champ}
                  type="password"
                  autoComplete="current-password"
                  invalide={Boolean(erreurs.motDePasse)}
                  value={motDePasse}
                  onChange={(evenement) => setMotDePasse(evenement.target.value)}
                />
              )}
            </FormField>

            <Button
              type="submit"
              variante="primaire"
              icone={SignIn}
              pleineLargeur
              enChargement={enCours}
              disabled={bloque}
            >
              Se connecter
            </Button>
          </form>
        </section>

        {COMPTES_DEMONSTRATION.length > 0 && (
          <section className="mt-4 rounded-carte border border-bordure bg-surface p-4">
            <h2 className="text-sm font-semibold text-marine">Comptes de démonstration</h2>
            <p className="mt-1 text-xs text-texte-secondaire">
              Affichés uniquement parce que les données sont simulées. Ils disparaissent dès que
              l&apos;application parle au vrai serveur.
            </p>
            <ul className="mt-3 space-y-1.5">
              {COMPTES_DEMONSTRATION.map((compte) => (
                <li key={compte.identifiant} className="flex items-center justify-between gap-3">
                  <span className="text-xs text-texte-secondaire">{compte.libelle}</span>
                  <button
                    type="button"
                    onClick={() => {
                      setIdentifiant(compte.identifiant)
                      setMotDePasse(compte.motDePasse)
                    }}
                    className="rounded-controle border border-bordure px-2 py-1 font-mono text-xs text-texte transition-colors hover:bg-fond focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sarcelle"
                  >
                    {compte.identifiant}
                  </button>
                </li>
              ))}
            </ul>
          </section>
        )}
      </div>
    </main>
  )
}
