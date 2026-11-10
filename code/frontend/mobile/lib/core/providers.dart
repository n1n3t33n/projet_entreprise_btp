import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import '../features/auth/application/controleur_auth.dart';
import '../features/auth/data/depot_session.dart';
import '../features/auth/data/service_auth.dart';
import '../features/auth/domain/etat_auth.dart';
import '../features/sync/data/depot_file_envoi.dart';
import 'api/client_api.dart';
import 'config/env.dart';
import 'db/base_locale.dart';
import 'securite/coffre.dart';

/// Composition racine des dépendances (injection par Riverpod).

final coffreProvider = Provider<Coffre>(
  (ref) => const Coffre(FlutterSecureStorage()),
);

final dioProvider = Provider<Dio>((ref) => creerDio());

/// Base locale chiffrée : fournie à l'amorçage (`main.dart`) une fois la clé
/// lue dans le coffre. Non résolue par défaut — toujours surchargée.
final baseLocaleProvider = Provider<BaseLocale>(
  (ref) => throw UnimplementedError(
    'baseLocaleProvider doit être surchargé au démarrage (main.dart).',
  ),
);

final serviceAuthProvider = Provider<ServiceAuth>((ref) {
  if (Env.apiSimulee) return const ServiceAuthSimule();
  return ServiceAuthHttp(ref.read(dioProvider));
});

final depotSessionProvider = Provider<DepotSession>(
  (ref) => DepotSession(ref.read(baseLocaleProvider)),
);

final depotFileEnvoiProvider = Provider<DepotFileEnvoi>(
  (ref) => DepotFileEnvoi(ref.read(baseLocaleProvider)),
);

final controleurAuthProvider = NotifierProvider<ControleurAuth, EtatAuth>(
  ControleurAuth.new,
);
