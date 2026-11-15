// Formes servies par l'API pour les comptes et la session, calquées sur le
// contrat du web (`features/auth/api/dto.ts`) : `snake_case` sur le fil,
// énumérés en `UPPER_SNAKE`. Le mot de passe ne circule que dans le corps de
// la requête de connexion ; il n'est jamais renvoyé ni stocké.

class UtilisateurDto {
  const UtilisateurDto({
    required this.idUtilisateur,
    required this.identifiant,
    required this.nom,
    required this.prenom,
    required this.fonction,
    required this.statut,
    required this.dateCreation,
    required this.roleCodeRole,
    required this.perimetreIdPerimetre,
    required this.libellePerimetre,
  });

  factory UtilisateurDto.fromJson(Map<String, dynamic> json) {
    return UtilisateurDto(
      idUtilisateur: json['id_utilisateur'] as String,
      identifiant: json['identifiant'] as String,
      nom: json['nom'] as String,
      prenom: json['prenom'] as String,
      fonction: json['fonction'] as String,
      statut: json['statut'] as String,
      dateCreation: json['date_creation'] as String,
      roleCodeRole: json['role_code_role'] as String,
      perimetreIdPerimetre: json['perimetre_id_perimetre'] as String,
      libellePerimetre: json['libelle_perimetre'] as String,
    );
  }

  final String idUtilisateur;
  final String identifiant;
  final String nom;
  final String prenom;
  final String fonction;

  /// `UPPER_SNAKE` : ACTIF, INACTIF.
  final String statut;
  final String dateCreation;

  /// Code du rôle affecté (table `role`).
  final String roleCodeRole;
  final String perimetreIdPerimetre;
  final String libellePerimetre;

  Map<String, dynamic> toJson() => {
    'id_utilisateur': idUtilisateur,
    'identifiant': identifiant,
    'nom': nom,
    'prenom': prenom,
    'fonction': fonction,
    'statut': statut,
    'date_creation': dateCreation,
    'role_code_role': roleCodeRole,
    'perimetre_id_perimetre': perimetreIdPerimetre,
    'libelle_perimetre': libellePerimetre,
  };
}

class SessionDto {
  const SessionDto({required this.jeton, required this.utilisateur});

  factory SessionDto.fromJson(Map<String, dynamic> json) {
    return SessionDto(
      jeton: json['jeton'] as String,
      utilisateur: UtilisateurDto.fromJson(
        json['utilisateur'] as Map<String, dynamic>,
      ),
    );
  }

  final String jeton;
  final UtilisateurDto utilisateur;

  Map<String, dynamic> toJson() => {
    'jeton': jeton,
    'utilisateur': utilisateur.toJson(),
  };
}

/// Corps d'erreur renvoyé par `POST /auth/connexion` en cas d'échec.
class EchecConnexionDto {
  const EchecConnexionDto({
    required this.motif,
    required this.message,
    this.secondesRestantes,
  });

  factory EchecConnexionDto.fromJson(Map<String, dynamic> json) {
    return EchecConnexionDto(
      motif: json['motif'] as String,
      message: json['message'] as String,
      secondesRestantes: json['secondes_restantes'] as int?,
    );
  }

  /// `IDENTIFIANTS`, `COMPTE_INACTIF` ou `VERROUILLE`.
  final String motif;
  final String message;
  final int? secondesRestantes;
}
