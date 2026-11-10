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

/// Implémentation HTTP réelle (branchée sur Django REST plus tard).
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
      return SessionDto.fromJson(reponse.data!);
    } on DioException catch (e) {
      final donnees = e.response?.data;
      if (donnees is Map<String, dynamic>) {
        throw EchecConnexionException(EchecConnexionDto.fromJson(donnees));
      }
      throw const EchecConnexionException(
        EchecConnexionDto(
          motif: 'IDENTIFIANTS',
          message: 'Connexion impossible. Vérifiez votre connexion.',
        ),
      );
    }
  }
}

/// Adaptateur simulé : tant que le serveur Django REST n'est pas disponible,
/// il rend une session fictive pour les comptes de démonstration du pilote de
/// Grand-Bassam. Activé par `Env.apiSimulee`.
class ServiceAuthSimule implements ServiceAuth {
  const ServiceAuthSimule();

  @override
  Future<SessionDto> connexion(String identifiant, String motDePasse) async {
    await Future<void>.delayed(const Duration(milliseconds: 300));

    if (motDePasse.isEmpty) {
      throw const EchecConnexionException(
        EchecConnexionDto(
          motif: 'IDENTIFIANTS',
          message: 'Identifiant ou mot de passe incorrect.',
        ),
      );
    }

    final role = _rolesDemo[identifiant] ?? 'MAGASINIER';
    return SessionDto(
      jeton: 'jeton-demo-$identifiant',
      utilisateur: UtilisateurDto(
        idUtilisateur: 'u-$identifiant',
        identifiant: identifiant,
        nom: 'Démonstration',
        prenom: identifiant,
        fonction: 'Agent de terrain',
        statut: 'ACTIF',
        dateCreation: DateTime(2026).toIso8601String(),
        roleCodeRole: role,
        perimetreIdPerimetre: 'perim-bassam',
        libellePerimetre: 'Chantier Grand-Bassam',
      ),
    );
  }

  /// Comptes de démonstration : un identifiant par rôle terrain.
  static const Map<String, String> _rolesDemo = {
    'magasinier': 'MAGASINIER',
    'technicien': 'TECHNICIEN',
    'chef': 'CHEF_CHANTIER',
    'gestionnaire': 'GESTIONNAIRE_STOCK',
    'responsable': 'RESPONSABLE_TECHNIQUE',
  };
}
