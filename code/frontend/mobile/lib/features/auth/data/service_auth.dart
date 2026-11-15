import 'package:dio/dio.dart';

import 'dto_auth.dart';

/// Levée quand la connexion en ligne échoue (identifiants, compte inactif,
/// verrouillage). Porte le corps d'erreur du serveur.
class EchecConnexionException implements Exception {
  const EchecConnexionException(this.echec);

  final EchecConnexionDto echec;

  @override
  String toString() => 'EchecConnexionException(${echec.motif})';
}

/// Contrat d'accès à l'authentification, au même format de routes que le web
/// (`POST /auth/connexion`).
abstract interface class ServiceAuth {
  Future<SessionDto> connexion(String identifiant, String motDePasse);
}

/// Implémentation HTTP réelle (branchée sur l'API quand elle sera disponible).
class ServiceAuthHttp implements ServiceAuth {
  const ServiceAuthHttp(this._dio);

  final Dio _dio;

  @override
  Future<SessionDto> connexion(String identifiant, String motDePasse) async {
    try {
      final reponse = await _dio.post<Map<String, dynamic>>(
        '/auth/connexion',
        data: {'identifiant': identifiant, 'mot_de_passe': motDePasse},
      );
      final corps = reponse.data;
      if (corps == null) {
        throw const EchecConnexionException(
          EchecConnexionDto(motif: 'RESEAU', message: 'Réponse vide.'),
        );
      }
      return SessionDto.fromJson(corps);
    } on DioException catch (e) {
      final donnees = e.response?.data;
      if (donnees is Map<String, dynamic>) {
        throw EchecConnexionException(EchecConnexionDto.fromJson(donnees));
      }
      throw const EchecConnexionException(
        EchecConnexionDto(motif: 'RESEAU', message: 'Connexion impossible.'),
      );
    }
  }
}

/// Compte de démonstration du pilote de Grand-Bassam.
class CompteDemonstration {
  const CompteDemonstration({
    required this.identifiant,
    required this.roleCode,
    required this.prenom,
    required this.nom,
    required this.fonction,
  });

  final String identifiant;
  final String roleCode;
  final String prenom;
  final String nom;
  final String fonction;
}

/// Adaptateur simulé : tant que le serveur n'est pas disponible, il rend une
/// session pour les comptes de démonstration (un par rôle de terrain). Activé
/// par `Env.apiSimulee` ; n'importe quel mot de passe non vide est accepté.
class ServiceAuthSimule implements ServiceAuth {
  const ServiceAuthSimule();

  static const List<CompteDemonstration> comptes = [
    CompteDemonstration(
      identifiant: 'magasinier',
      roleCode: 'MAGASINIER',
      prenom: 'Mamadou',
      nom: 'Koné',
      fonction: 'Magasinier',
    ),
    CompteDemonstration(
      identifiant: 'technicien',
      roleCode: 'TECHNICIEN',
      prenom: 'Kouassi',
      nom: 'Adama',
      fonction: "Chef d'équipe maçonnerie",
    ),
    CompteDemonstration(
      identifiant: 'chef',
      roleCode: 'CHEF_CHANTIER',
      prenom: 'Mamadou',
      nom: 'Traoré',
      fonction: 'Chef de chantier',
    ),
    CompteDemonstration(
      identifiant: 'gestionnaire',
      roleCode: 'GESTIONNAIRE_STOCK',
      prenom: 'Idriss',
      nom: 'Sékou',
      fonction: 'Gestionnaire de stock',
    ),
    CompteDemonstration(
      identifiant: 'responsable',
      roleCode: 'RESPONSABLE_TECHNIQUE',
      prenom: 'Awa',
      nom: 'Bamba',
      fonction: 'Responsable technique',
    ),
  ];

  @override
  Future<SessionDto> connexion(String identifiant, String motDePasse) async {
    await Future<void>.delayed(const Duration(milliseconds: 350));

    final compte = comptes
        .where((c) => c.identifiant == identifiant.toLowerCase())
        .firstOrNull;
    if (compte == null || motDePasse.isEmpty) {
      throw const EchecConnexionException(
        EchecConnexionDto(
          motif: 'IDENTIFIANTS',
          message: 'Identifiant ou mot de passe incorrect.',
        ),
      );
    }

    return SessionDto(
      jeton: 'jeton-demo-${compte.identifiant}',
      utilisateur: UtilisateurDto(
        idUtilisateur: 'u-${compte.identifiant}',
        identifiant: compte.identifiant,
        nom: compte.nom,
        prenom: compte.prenom,
        fonction: compte.fonction,
        statut: 'ACTIF',
        dateCreation: DateTime(2026).toIso8601String(),
        roleCodeRole: compte.roleCode,
        perimetreIdPerimetre: 'CH-GB',
        libellePerimetre: 'Chantier de Grand-Bassam',
      ),
    );
  }
}
