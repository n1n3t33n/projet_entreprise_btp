// Identité affichable de l'opérateur connecté, conservée sur l'appareil pour
// l'usage hors-ligne : nom, fonction et périmètre (chantier). Aucun secret.

class ProfilUtilisateur {
  const ProfilUtilisateur({
    required this.idUtilisateur,
    required this.identifiant,
    required this.prenom,
    required this.nom,
    required this.fonction,
    required this.perimetre,
  });

  factory ProfilUtilisateur.fromJson(Map<String, dynamic> json) {
    return ProfilUtilisateur(
      idUtilisateur: json['id_utilisateur'] as String,
      identifiant: json['identifiant'] as String,
      prenom: json['prenom'] as String,
      nom: json['nom'] as String,
      fonction: json['fonction'] as String,
      perimetre: json['libelle_perimetre'] as String,
    );
  }

  final String idUtilisateur;
  final String identifiant;
  final String prenom;
  final String nom;
  final String fonction;

  /// Libellé du périmètre d'affectation (« Chantier de Grand-Bassam »).
  final String perimetre;

  String get nomComplet => '$prenom $nom'.trim();

  Map<String, dynamic> toJson() => {
    'id_utilisateur': idUtilisateur,
    'identifiant': identifiant,
    'prenom': prenom,
    'nom': nom,
    'fonction': fonction,
    'libelle_perimetre': perimetre,
  };
}
