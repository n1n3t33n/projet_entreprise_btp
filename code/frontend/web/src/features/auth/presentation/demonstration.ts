/*
  Comptes de démonstration proposés sur l'écran de connexion.

  Ils ne sont renseignés QUE lorsque l'adaptateur de simulation est branché :
  dès que l'application parle au vrai serveur, la liste est vide et l'encart
  disparaît de l'écran. Aucun identifiant réel ne figure donc jamais ici.
*/

import { mocksActifs } from '@/lib/mocks'
import { MOT_DE_PASSE_DEMONSTRATION } from '@/lib/mocks/auth-grand-bassam'
import { tr } from '@/i18n/tr'

export type CompteDemonstration = {
  identifiant: string
  motDePasse: string
  libelle: string
}

const COMPTES: CompteDemonstration[] = [
  { identifiant: 'a.kouassi', motDePasse: MOT_DE_PASSE_DEMONSTRATION, libelle: tr('Direction') },
  { identifiant: 'y.bamba', motDePasse: MOT_DE_PASSE_DEMONSTRATION, libelle: tr('Administrateur') },
  {
    identifiant: 'k.n-guessan',
    motDePasse: MOT_DE_PASSE_DEMONSTRATION,
    libelle: tr('Responsable technique'),
  },
  { identifiant: 's.traore', motDePasse: MOT_DE_PASSE_DEMONSTRATION, libelle: tr('Commercial') },
  { identifiant: 'm.diallo', motDePasse: MOT_DE_PASSE_DEMONSTRATION, libelle: tr('Acquéreur') },
]

export const COMPTES_DEMONSTRATION: CompteDemonstration[] = mocksActifs() ? COMPTES : []
