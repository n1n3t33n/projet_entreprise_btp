import '../roles/role_terrain.dart';
import 'ecran_mobile.dart';

/// Cloisonnement des accès par rôle (navigation basse filtrée).
///
/// PROVISOIRE (M1) : cette table reproduit l'intention des accueils par rôle
/// des wireframes (A1–A5). À terme, l'accès est une DONNÉE servie par l'API des
/// droits (comme le web : la matrice vient de `features/admin/api`). Cette
/// configuration locale sera remplacée par la matrice distante dès que la
/// couche droits sera branchée — aucune règle d'accès n'est figée dans le code
/// métier.
abstract final class AccesParRole {
  static const Map<RoleTerrain, List<EcranMobile>> _ecrans = {
    // A1 — Magasinier : stock et mouvements.
    RoleTerrain.magasinier: [
      EcranMobile.accueil,
      EcranMobile.stock,
      EcranMobile.mouvements,
      EcranMobile.synchronisation,
    ],
    // A2 — Technicien : fiche de route et étapes.
    RoleTerrain.technicien: [
      EcranMobile.accueil,
      EcranMobile.ficheRoute,
      EcranMobile.etapes,
      EcranMobile.synchronisation,
    ],
    // A3 — Chef de chantier : étapes et validation.
    RoleTerrain.chefChantier: [
      EcranMobile.accueil,
      EcranMobile.etapes,
      EcranMobile.validation,
      EcranMobile.synchronisation,
    ],
    // A4 — Gestionnaire de stock : stock et validation.
    RoleTerrain.gestionnaireStock: [
      EcranMobile.accueil,
      EcranMobile.stock,
      EcranMobile.validation,
      EcranMobile.synchronisation,
    ],
    // A5 — Responsable technique : étapes et validation (portée allégée).
    RoleTerrain.responsableTechnique: [
      EcranMobile.accueil,
      EcranMobile.etapes,
      EcranMobile.validation,
      EcranMobile.synchronisation,
    ],
  };

  /// Écrans autorisés pour [role], dans l'ordre d'affichage de la barre basse.
  /// Au minimum l'accueil, si un rôle n'était pas cartographié.
  static List<EcranMobile> ecransAutorises(RoleTerrain role) {
    return _ecrans[role] ?? const [EcranMobile.accueil];
  }
}
