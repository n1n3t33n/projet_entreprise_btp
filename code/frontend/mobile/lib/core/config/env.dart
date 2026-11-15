/// Configuration d'environnement, fournie à la compilation
/// (`--dart-define=API_BASE_URL=...`). Ce ne sont pas des secrets : seulement
/// l'adresse du serveur. Les secrets d'exécution vivent dans le coffre.
abstract final class Env {
  /// Base de l'API ChantierSync (même contrat de routes que le web).
  /// HTTPS imposé : aucune adresse en clair en production.
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'https://api.chantiersync.local/api',
  );

  /// Active l'adaptateur simulé tant que le backend Django REST n'est pas là.
  static const bool apiSimulee = bool.fromEnvironment(
    'API_SIMULEE',
    defaultValue: true,
  );
}
