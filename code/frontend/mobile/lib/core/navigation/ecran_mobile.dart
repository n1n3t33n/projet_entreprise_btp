import 'package:flutter/widgets.dart';
import 'package:phosphor_flutter/phosphor_flutter.dart';

/// Catalogue des écrans de l'application mobile de terrain.
///
/// Ce catalogue décrit UNIQUEMENT l'existence des écrans (identifiant, libellé,
/// icône, chemin). Il ne dit pas qui y a accès : le cloisonnement par rôle est
/// une donnée (voir [AccesParRole]), conformément à la décision « données en
/// base et non du code » et au fonctionnement du web (config/navigation.ts).
///
/// Au jalon M1 (socle), seuls `accueil` et `synchronisation` sont actifs ; les
/// écrans métier (stock, mouvements, étapes, validation, fiche de route) sont
/// des emplacements réservés, activés aux jalons M2 et M3.
enum EcranMobile {
  accueil('accueil', 'Accueil', '/accueil'),
  stock('stock', 'Stock', '/stock'),
  mouvements('mouvements', 'Mouvements', '/mouvements'),
  ficheRoute('fiche-route', 'Fiche de route', '/fiche-route'),
  etapes('etapes', 'Étapes', '/etapes'),
  validation('validation', 'Validation', '/validation'),
  synchronisation('synchronisation', 'Synchronisation', '/synchronisation');

  const EcranMobile(this.id, this.libelle, this.chemin);

  final String id;
  final String libelle;
  final String chemin;

  /// Icône Phosphor (style outline, charte § 4).
  IconData get icone => switch (this) {
    EcranMobile.accueil => PhosphorIconsRegular.house,
    EcranMobile.stock => PhosphorIconsRegular.package,
    EcranMobile.mouvements => PhosphorIconsRegular.arrowsLeftRight,
    EcranMobile.ficheRoute => PhosphorIconsRegular.clipboardText,
    EcranMobile.etapes => PhosphorIconsRegular.listChecks,
    EcranMobile.validation => PhosphorIconsRegular.checkCircle,
    EcranMobile.synchronisation => PhosphorIconsRegular.arrowsClockwise,
  };

  /// Vrai si l'écran porte une fonctionnalité métier non encore livrée en M1.
  bool get reserveJalonSuivant => switch (this) {
    EcranMobile.accueil || EcranMobile.synchronisation => false,
    _ => true,
  };
}
