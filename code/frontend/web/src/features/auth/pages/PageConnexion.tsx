/*
  Écran de connexion du poste de pilotage (charte § 9.2, écran 1 ;
  EF-AUT-04 : identifiant et mot de passe, verrouillage temporaire après
  échecs répétés).

  Page volontairement sobre : un en-tête fin, le logo, le formulaire. Aucun
  slogan ni décor — c'est une porte d'entrée de bureau, pas une vitrine.
  Validation en ligne, message d'échec distinct selon le motif renvoyé par le
  serveur. Pendant un verrouillage, le formulaire reste visible mais la
  soumission est refusée, avec le temps d'attente restant.
*/

import { useEffect, useState, type FormEvent } from 'react'
import { Navigate } from 'react-router-dom'
import { LockKey, MapPin, SignIn, Warning } from '@phosphor-icons/react'
import { Button, FormField, Input } from '@/components/ui'
import { Logo } from '@/components/ui/Logo'
import { useT } from '@/app/preferences-context'
import { Reglages } from '@/app/Reglages'
import { useSession } from '@/app/session-context'
import { ErreurConnexion, seConnecter } from '@/features/auth/api'
import { COMPTES_DEMONSTRATION } from '@/features/auth/presentation/demonstration'
import type { EchecConnexion } from '@/features/auth/types/domaine'

export function PageConnexion() {
  const { connecte, ouvrirSession } = useSession()
  const t = useT()

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
      prochaines.identifiant = t.connexion.saisirIdentifiant
    }
    if (motDePasse === '') {
      prochaines.motDePasse = t.connexion.saisirMotDePasse
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
        setEchec({ motif: 'identifiants', message: t.connexion.echec })
      }
      setMotDePasse('')
    } finally {
      setEnCours(false)
    }
  }

  const bloque = attente > 0

  return (
    <div className="flex min-h-dvh flex-col bg-fond">
      <header className="flex items-center justify-between gap-4 border-b border-bordure bg-surface px-6 py-3">
        <p className="text-sm font-medium text-texte-secondaire">{t.connexion.entite}</p>
        <Reglages />
      </header>

      <main className="flex flex-1 items-center justify-center px-4 py-10">
        <div className="w-full max-w-sm">
          <div className="flex justify-center">
            <Logo avecSousTitre={false} />
          </div>

          <h1 className="mt-8 text-2xl font-bold text-marine">{t.connexion.titre}</h1>
          <p className="mt-1 flex items-center gap-1.5 text-sm text-texte-secondaire">
            <MapPin size={16} weight="regular" aria-hidden className="shrink-0" />
            {t.coquille.chantierPilote}
          </p>

          {echec && (
            <p
              role="alert"
              className="mt-5 flex items-start gap-2 rounded-controle border border-danger/30 bg-danger/5 px-3 py-2 text-sm font-medium text-danger"
            >
              {bloque ? (
                <LockKey size={16} weight="regular" aria-hidden className="mt-0.5 shrink-0" />
              ) : (
                <Warning size={16} weight="regular" aria-hidden className="mt-0.5 shrink-0" />
              )}
              <span>
                {echec.message}
                {bloque && ` ${t.connexion.reessayer.replace('{n}', String(attente))}`}
              </span>
            </p>
          )}

          <form onSubmit={soumettre} className="mt-6 flex flex-col gap-4" noValidate>
            <FormField libelle={t.connexion.identifiant} requis erreur={erreurs.identifiant}>
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

            <FormField libelle={t.connexion.motDePasse} requis erreur={erreurs.motDePasse}>
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
              taille="lg"
              icone={SignIn}
              pleineLargeur
              enChargement={enCours}
              disabled={bloque}
            >
              {t.connexion.seConnecter}
            </Button>
          </form>

          <p className="mt-5 text-sm text-texte-secondaire">{t.connexion.aideAcces}</p>

          {COMPTES_DEMONSTRATION.length > 0 && (
            <details className="mt-8 border-t border-bordure pt-4 text-sm">
              <summary className="cursor-pointer font-medium text-texte-secondaire hover:text-texte focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sarcelle">
                {t.connexion.demoTitre}
              </summary>
              <p className="mt-2 text-xs text-texte-secondaire">{t.connexion.demoAide}</p>
              <ul className="mt-3 divide-y divide-bordure">
                {COMPTES_DEMONSTRATION.map((compte) => (
                  <li key={compte.identifiant}>
                    <button
                      type="button"
                      onClick={() => {
                        setIdentifiant(compte.identifiant)
                        setMotDePasse(compte.motDePasse)
                      }}
                      className="flex w-full items-center justify-between gap-3 py-2 text-left transition-colors duration-[var(--duree-bouton)] hover:text-marine focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sarcelle"
                    >
                      <span>{compte.libelle}</span>
                      <span className="font-mono text-xs text-texte-secondaire">
                        {compte.identifiant}
                      </span>
                    </button>
                  </li>
                ))}
              </ul>
            </details>
          )}
        </div>
      </main>

      <footer className="px-6 py-4 text-center text-xs text-texte-secondaire">
        {t.connexion.sousTitre}
      </footer>
    </div>
  )
}
