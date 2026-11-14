import 'package:flutter/widgets.dart';
import 'package:phosphor_flutter/phosphor_flutter.dart';

import '../../l10n/traductions.dart';
import '../roles/role_terrain.dart';

/// Onglets de la barre de navigation basse.
///
/// Le premier onglet d'un rôle est toujours son tableau de bord : « Stock »
/// pour le magasinier, « Fiches » pour le technicien, « À valider » pour ceux
/// qui contrôlent (maquettes A1 à A5).
enum OngletRole {
  stock,
  fiches,
  aValider,
  historique,
  synchro,
  profil;

  IconData get icone => switch (this) {
    OngletRole.stock => PhosphorIconsRegular.package,
    OngletRole.fiches => PhosphorIconsRegular.clipboardText,
    OngletRole.aValider => PhosphorIconsRegular.sealCheck,
    OngletRole.historique => PhosphorIconsRegular.clockCounterClockwise,
    OngletRole.synchro => PhosphorIconsRegular.arrowsClockwise,
    OngletRole.profil => PhosphorIconsRegular.userCircle,
  };

  IconData get iconeActive => switch (this) {
    OngletRole.stock => PhosphorIconsFill.package,
    OngletRole.fiches => PhosphorIconsFill.clipboardText,
    OngletRole.aValider => PhosphorIconsFill.sealCheck,
    OngletRole.historique => PhosphorIconsFill.clockCounterClockwise,
    OngletRole.synchro => PhosphorIconsFill.arrowsClockwise,
    OngletRole.profil => PhosphorIconsFill.userCircle,
  };

  String libelle(Traductions t) => switch (this) {
    OngletRole.stock => t.ongletStock,
    OngletRole.fiches => t.ongletFiches,
    OngletRole.aValider => t.ongletAValider,
    OngletRole.historique => t.ongletHistorique,
    OngletRole.synchro => t.ongletSynchro,
    OngletRole.profil => t.ongletProfil,
  };
}

/// Libellé traduit d'un rôle de terrain (jamais son code interne, charte § 8).
String libelleRole(Traductions t, RoleTerrain role) => switch (role) {
  RoleTerrain.magasinier => t.roleMagasinier,
  RoleTerrain.technicien => t.roleTechnicien,
  RoleTerrain.chefChantier => t.roleChefChantier,
  RoleTerrain.gestionnaireStock => t.roleGestionnaireStock,
  RoleTerrain.responsableTechnique => t.roleResponsableTechnique,
};

/// Cloisonnement de la navigation par rôle (charte § 9.3).
///
/// PROVISOIRE : cette table reprend les maquettes. À terme l'accès est une
/// donnée servie par l'API des droits, comme sur le poste de pilotage web ;
/// seule cette fonction sera alors à remplacer.
List<OngletRole> ongletsPour(RoleTerrain role) => switch (role) {
  RoleTerrain.magasinier => const [
    OngletRole.stock,
    OngletRole.historique,
    OngletRole.synchro,
    OngletRole.profil,
  ],
  RoleTerrain.gestionnaireStock => const [
    OngletRole.stock,
    OngletRole.aValider,
    OngletRole.historique,
    OngletRole.profil,
  ],
  RoleTerrain.technicien => const [
    OngletRole.fiches,
    OngletRole.historique,
    OngletRole.synchro,
    OngletRole.profil,
  ],
  RoleTerrain.chefChantier => const [
    OngletRole.aValider,
    OngletRole.fiches,
    OngletRole.stock,
    OngletRole.profil,
  ],
  RoleTerrain.responsableTechnique => const [
    OngletRole.aValider,
    OngletRole.fiches,
    OngletRole.profil,
  ],
};
