/*
  Textes de l'interface, en français (référence), anglais et italien.

  Le français définit la forme : les deux autres langues sont typées sur lui,
  donc une clé oubliée ne compile pas. Les données métier (désignations
  d'articles, noms de personnes) ne sont pas traduites.
*/

const fr = {
  marque: { sousTitre: 'ChantierSync · Poste de pilotage' },
  navigation: {
    principale: 'Navigation principale',
    'tableau-de-bord': 'Tableau de bord',
    avancement: 'Avancement',
    journal: "Journal d'exécution",
    stock: 'Stock',
    referentiels: 'Référentiels',
    gammes: 'Gammes',
    equipes: 'Équipes',
    parametrage: 'Paramétrage',
    administration: 'Administration',
    synchronisation: 'Synchronisation',
    'espace-acquereur': 'Espace acquéreur',
  },
  roles: {
    direction: 'Direction',
    administrateur: 'Administrateur',
    commercial: 'Commercial',
    responsable_technique: 'Responsable technique',
    acquereur: 'Acquéreur',
  },
  coquille: {
    utilisateur: 'Utilisateur',
    deconnexion: 'Se déconnecter',
    role: 'Rôle',
    chantierPilote: 'Chantier de Grand-Bassam',
    recherche: 'Recherche globale — bientôt disponible',
    notifications: 'Notifications : bientôt disponible',
    aide: 'Aide : bientôt disponible',
  },
  reglages: {
    titre: 'Affichage',
    langue: 'Langue',
    theme: 'Apparence',
    clair: 'Clair',
    sombre: 'Sombre',
    systeme: 'Automatique',
  },
  connexion: {
    titre: 'Poste de pilotage',
    entite: 'Schiavone Group · Italia Construction',
    sousTitre: 'ChantierSync — accès réservé aux comptes nominatifs.',
    aideAcces: 'Identifiants oubliés ? Voyez l’administrateur du chantier.',
    identifiant: 'Identifiant',
    motDePasse: 'Mot de passe',
    seConnecter: 'Se connecter',
    saisirIdentifiant: 'Saisir un identifiant.',
    saisirMotDePasse: 'Saisir un mot de passe.',
    echec: 'La connexion a échoué.',
    reessayer: 'Réessayez dans {n} s.',
    demoTitre: 'Comptes de démonstration',
    demoAide:
      "Affichés uniquement parce que les données sont simulées. Ils disparaissent dès que l'application parle au vrai serveur.",
  },
}

export type Dictionnaire = typeof fr

const en: Dictionnaire = {
  marque: { sousTitre: 'ChantierSync · Control desk' },
  navigation: {
    principale: 'Main navigation',
    'tableau-de-bord': 'Dashboard',
    avancement: 'Progress',
    journal: 'Execution log',
    stock: 'Stock',
    referentiels: 'Reference data',
    gammes: 'Work methods',
    equipes: 'Crews',
    parametrage: 'Settings',
    administration: 'Administration',
    synchronisation: 'Synchronisation',
    'espace-acquereur': 'Buyer area',
  },
  roles: {
    direction: 'Management',
    administrateur: 'Administrator',
    commercial: 'Sales',
    responsable_technique: 'Technical lead',
    acquereur: 'Buyer',
  },
  coquille: {
    utilisateur: 'User',
    deconnexion: 'Sign out',
    role: 'Role',
    chantierPilote: 'Grand-Bassam site',
    recherche: 'Global search — coming soon',
    notifications: 'Notifications: coming soon',
    aide: 'Help: coming soon',
  },
  reglages: {
    titre: 'Display',
    langue: 'Language',
    theme: 'Appearance',
    clair: 'Light',
    sombre: 'Dark',
    systeme: 'Automatic',
  },
  connexion: {
    titre: 'Control desk',
    entite: 'Schiavone Group · Italia Construction',
    sousTitre: 'ChantierSync — access limited to named accounts.',
    aideAcces: 'Forgot your sign-in details? Ask the site administrator.',
    identifiant: 'Username',
    motDePasse: 'Password',
    seConnecter: 'Sign in',
    saisirIdentifiant: 'Enter a username.',
    saisirMotDePasse: 'Enter a password.',
    echec: 'Sign-in failed.',
    reessayer: 'Try again in {n} s.',
    demoTitre: 'Demo accounts',
    demoAide:
      'Shown only because the data is simulated. They disappear as soon as the app talks to the real server.',
  },
}

const it: Dictionnaire = {
  marque: { sousTitre: 'ChantierSync · Postazione di controllo' },
  navigation: {
    principale: 'Navigazione principale',
    'tableau-de-bord': 'Cruscotto',
    avancement: 'Avanzamento',
    journal: 'Registro di esecuzione',
    stock: 'Magazzino',
    referentiels: 'Anagrafiche',
    gammes: 'Procedure',
    equipes: 'Squadre',
    parametrage: 'Impostazioni',
    administration: 'Amministrazione',
    synchronisation: 'Sincronizzazione',
    'espace-acquereur': 'Area acquirente',
  },
  roles: {
    direction: 'Direzione',
    administrateur: 'Amministratore',
    commercial: 'Commerciale',
    responsable_technique: 'Responsabile tecnico',
    acquereur: 'Acquirente',
  },
  coquille: {
    utilisateur: 'Utente',
    deconnexion: 'Esci',
    role: 'Ruolo',
    chantierPilote: 'Cantiere di Grand-Bassam',
    recherche: 'Ricerca globale — presto disponibile',
    notifications: 'Notifiche: presto disponibili',
    aide: 'Aiuto: presto disponibile',
  },
  reglages: {
    titre: 'Visualizzazione',
    langue: 'Lingua',
    theme: 'Aspetto',
    clair: 'Chiaro',
    sombre: 'Scuro',
    systeme: 'Automatico',
  },
  connexion: {
    titre: 'Postazione di controllo',
    entite: 'Schiavone Group · Italia Construction',
    sousTitre: 'ChantierSync — accesso riservato agli account nominativi.',
    aideAcces: 'Credenziali dimenticate? Rivolgiti all’amministratore del cantiere.',
    identifiant: 'Nome utente',
    motDePasse: 'Password',
    seConnecter: 'Accedi',
    saisirIdentifiant: 'Inserire un nome utente.',
    saisirMotDePasse: 'Inserire una password.',
    echec: 'Accesso non riuscito.',
    reessayer: 'Riprova tra {n} s.',
    demoTitre: 'Account dimostrativi',
    demoAide:
      "Visibili solo perché i dati sono simulati. Spariscono appena l'app comunica con il server reale.",
  },
}

export type Langue = 'fr' | 'en' | 'it'

export const LANGUES: { code: Langue; nom: string }[] = [
  { code: 'fr', nom: 'Français' },
  { code: 'en', nom: 'English' },
  { code: 'it', nom: 'Italiano' },
]

export const DICTIONNAIRES: Record<Langue, Dictionnaire> = { fr, en, it }

/** Vrai si la chaîne désigne une langue proposée. */
export function estLangue(valeur: string | null): valeur is Langue {
  return valeur === 'fr' || valeur === 'en' || valeur === 'it'
}
