// Verrou de session locale (AC-1 / ET-4).
//
// Une session hors-ligne reste valide 14 jours après la dernière connexion en
// ligne. Au-delà, l'appareil doit se reconnecter au serveur. Fonctions pures,
// sans dépendance Flutter : testables directement.

/// Durée d'autonomie hors-ligne avant reconnexion obligatoire.
const Duration dureeVerrouSession = Duration(days: 14);

/// Vrai si le verrou a expiré à l'instant [maintenant].
bool verrouExpire(
  DateTime derniereConnexionEnLigne,
  DateTime maintenant, {
  Duration duree = dureeVerrouSession,
}) {
  final echeance = derniereConnexionEnLigne.add(duree);
  return !maintenant.isBefore(echeance);
}

/// Temps restant avant expiration (zéro si déjà expiré).
Duration tempsRestantVerrou(
  DateTime derniereConnexionEnLigne,
  DateTime maintenant, {
  Duration duree = dureeVerrouSession,
}) {
  final restant = derniereConnexionEnLigne.add(duree).difference(maintenant);
  return restant.isNegative ? Duration.zero : restant;
}
