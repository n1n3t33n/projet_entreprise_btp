import type { Role } from '@/app/role-context'
import type { UrgenceAlerte } from '@/lib/seuils'

/*
  Paramètres réglables de l'application.

  Tout ce qui relève d'un choix d'exploitation — un facteur de seuil, une
  fréquence de rappel, une liste de destinataires, une durée d'affichage — est
  déclaré ici et nulle part ailleurs. Aucun composant ne lit ce fichier : un
  écran ou un fournisseur le consulte et transmet la valeur par propriété, pour
  qu'un composant reste réutilisable dans un contexte où le paramètre serait
  différent.

  Ces valeurs s'appliquent tant que l'API ne sert pas la configuration de
  l'entreprise. Elles ont vocation à être remplacées par la réponse de
  l'endpoint de paramétrage, puis à devenir modifiables depuis l'écran
  d'administration.
*/

export type ParametresStock = {
  /**
   * Facteur appliqué au seuil d'alerte pour proposer un seuil de confort.
   *
   * Le seuil de confort est une donnée du référentiel, portée par chaque
   * article. Ce facteur ne s'y substitue pas : il sert à pré-remplir le champ
   * au moment où l'article est créé, et de valeur de repli à l'affichage pour
   * une fiche enregistrée avant que le champ n'existe.
   */
  facteurSeuilConfortParDefaut: number
}

/** Valeur indexée par degré d'urgence, hors niveau qui ne déclenche rien. */
type ParUrgence<T> = Record<Exclude<UrgenceAlerte, 'aucune'>, T>

/** Heures écoulées entre deux rappels, selon l'urgence du niveau atteint. */
export type IntervallesRappel = ParUrgence<number>

/**
 * Rôles prévenus à chaque degré d'urgence.
 *
 * Les adresses ne sont pas stockées ici : elles viennent du compte de chaque
 * utilisateur. L'administrateur choisit les rôles concernés, et le serveur
 * résout la liste des adresses au moment de l'envoi. L'acquéreur, qui consulte
 * sans intervenir sur le stock, n'y figure jamais.
 */
export type DestinatairesAlertes = ParUrgence<Role[]>

/**
 * Remontée d'une alerte restée sans suite.
 *
 * Un rappel que personne ne traite finit par être ignoré. Passé un certain
 * nombre de relances sans effet, la question n'est plus d'informer mais de
 * faire décider : l'alerte part alors aussi vers les rôles indiqués ici, qui
 * s'ajoutent aux destinataires habituels sans les remplacer.
 *
 * Fonction optionnelle, désactivée par défaut, activée depuis l'écran
 * d'administration.
 */
export type ParametresEscalade = {
  /** Interrupteur exposé à l'administrateur. */
  activee: boolean
  /**
   * Nombre de rappels restés sans suite avant la remontée.
   *
   * Un rappel est tenu pour sans suite tant que le niveau d'alerte n'a pas été
   * quitté et qu'aucune demande de réapprovisionnement n'a été créée sur
   * l'article.
   */
  rappelsAvantDeclenchement: number
  /** Rôles ajoutés aux destinataires lorsque la remontée se déclenche. */
  roles: Role[]
}

export type ParametresAlertes = {
  /** Fréquence des rappels tant que le niveau reste atteint. */
  intervalleRappelHeures: IntervallesRappel
  /** Rôles prévenus, par degré d'urgence. */
  destinatairesParUrgence: DestinatairesAlertes
  /** Remontée aux responsables quand les rappels restent sans suite. */
  escalade: ParametresEscalade
  /**
   * Suspend les rappels d'un article dès qu'une demande de réapprovisionnement
   * est en cours pour cet article.
   */
  suspendreSiReapprovisionnementEnCours: boolean
  /** Canaux de diffusion activés. */
  canaux: {
    /** Notification dans l'application, visible à la connexion. */
    inApp: boolean
    /** Courriel envoyé à l'adresse du compte des rôles retenus. */
    email: boolean
  }
}

export type ParametresNotifications = {
  /** Durée d'affichage par défaut d'une notification brève, en millisecondes. */
  dureeToastMs: number
}

export type ParametresApplication = {
  stock: ParametresStock
  alertes: ParametresAlertes
  notifications: ParametresNotifications
}

export const PARAMETRES_PAR_DEFAUT: ParametresApplication = {
  stock: {
    facteurSeuilConfortParDefaut: 2,
  },
  alertes: {
    intervalleRappelHeures: {
      surveillance: 24,
      urgente: 6,
      immediate: 2,
    },
    destinatairesParUrgence: {
      surveillance: ['responsable_technique'],
      urgente: ['responsable_technique', 'administrateur'],
      immediate: ['responsable_technique', 'administrateur', 'direction'],
    },
    escalade: {
      // Option proposée à l'administrateur, inactive tant qu'il ne l'active pas.
      activee: false,
      rappelsAvantDeclenchement: 3,
      roles: ['direction'],
    },
    suspendreSiReapprovisionnementEnCours: true,
    canaux: {
      inApp: true,
      email: false,
    },
  },
  notifications: {
    dureeToastMs: 5000,
  },
}

/**
 * Seuil de confort retenu pour un article.
 *
 * Le référentiel fait foi : un article porte son propre seuil. La valeur de
 * repli n'intervient que pour une fiche qui n'en a pas encore, et reste un
 * paramètre modifiable plutôt qu'une constante enfouie dans un composant.
 */
export function resoudreSeuilConfort(
  seuilMini: number,
  seuilConfortArticle: number | null | undefined,
  parametres: ParametresStock = PARAMETRES_PAR_DEFAUT.stock,
): number {
  if (seuilConfortArticle !== null && seuilConfortArticle !== undefined) {
    return seuilConfortArticle
  }
  return seuilMini * parametres.facteurSeuilConfortParDefaut
}

/**
 * Rôles à prévenir pour une alerte, escalade comprise.
 *
 * `nombreRappelsEnvoyes` compte les rappels déjà partis sans qu'aucune suite
 * n'ait été donnée. Tant que l'escalade est désactivée, la fonction renvoie
 * simplement les destinataires du degré d'urgence.
 */
export function destinatairesAlerte(
  urgence: Exclude<UrgenceAlerte, 'aucune'>,
  nombreRappelsEnvoyes: number,
  parametres: ParametresAlertes = PARAMETRES_PAR_DEFAUT.alertes,
): Role[] {
  const destinataires = parametres.destinatairesParUrgence[urgence]
  const { escalade } = parametres

  const remonteeDeclenchee =
    escalade.activee && nombreRappelsEnvoyes >= escalade.rappelsAvantDeclenchement

  if (!remonteeDeclenchee) {
    return destinataires
  }

  const ajouts = escalade.roles.filter((role) => !destinataires.includes(role))
  return [...destinataires, ...ajouts]
}
