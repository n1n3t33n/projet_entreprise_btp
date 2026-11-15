/// Rôles de terrain de ChantierSync (portée mobile).
///
/// Mêmes rôles que le web, transposés au terrain (charte § 9.3). Le code de
/// rôle circule en `UPPER_SNAKE`, comme les énumérés servis par l'API
/// (cf. contrat web `features/auth/api/dto.ts`).
enum RoleTerrain {
  magasinier('MAGASINIER', 'Magasinier'),
  technicien('TECHNICIEN', 'Technicien'),
  chefChantier('CHEF_CHANTIER', 'Chef de chantier'),
  gestionnaireStock('GESTIONNAIRE_STOCK', 'Gestionnaire de stock'),
  responsableTechnique('RESPONSABLE_TECHNIQUE', 'Responsable technique');

  const RoleTerrain(this.code, this.libelle);

  /// Code serveur (`role_code_role`).
  final String code;

  /// Libellé affiché à l'écran.
  final String libelle;

  /// Retrouve un rôle terrain par son code serveur, ou `null` si inconnu
  /// (par exemple un rôle purement bureau : Direction, Administrateur…).
  static RoleTerrain? parCode(String code) {
    for (final role in RoleTerrain.values) {
      if (role.code == code) return role;
    }
    return null;
  }
}
