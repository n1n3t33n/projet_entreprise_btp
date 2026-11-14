import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import '../features/auth/application/controleur_auth.dart';
import '../features/auth/data/depot_session.dart';
import '../features/auth/data/service_auth.dart';
import '../features/auth/domain/etat_auth.dart';
import '../features/auth/domain/profil_utilisateur.dart';
import '../features/sync/data/depot_file_envoi.dart';
import 'api/client_api.dart';
import 'config/env.dart';
import 'db/base_locale.dart';
import 'roles/role_terrain.dart';
import 'securite/coffre.dart';
import 'stockage/magasin_documents.dart';
import 'stockage/magasin_documents_drift.dart';

/// Composition racine des dépendances (injection par Riverpod).
///
/// Chaque brique est un contrat : l'application branche les implémentations
/// réelles (base chiffrée, coffre), les tests branchent des doublures en
/// mémoire en surchargeant ces fournisseurs.

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

/// Identifiant court de l'appareil, affiché à l'opérateur.
final idAppareilProvider = Provider<String>((ref) => 'T-000');

final magasinDocumentsProvider = Provider<MagasinDocuments>(
  (ref) => MagasinDocumentsDrift(ref.read(baseLocaleProvider)),
);

final serviceAuthProvider = Provider<ServiceAuth>((ref) {
  if (Env.apiSimulee) return const ServiceAuthSimule();
  return ServiceAuthHttp(ref.read(dioProvider));
});

final depotSessionProvider = Provider<DepotSession>(
  (ref) => DepotSessionDrift(
    ref.read(baseLocaleProvider),
    ref.read(magasinDocumentsProvider),
  ),
);

final depotFileEnvoiProvider = Provider<DepotFileEnvoi>(
  (ref) => DepotFileEnvoiDrift(ref.read(baseLocaleProvider)),
);

final controleurAuthProvider = NotifierProvider<ControleurAuth, EtatAuth>(
  ControleurAuth.new,
);

/// Contenu de la file d'envoi. À invalider après chaque saisie ou envoi pour
/// que les bandeaux et compteurs se mettent à jour.
final fileEnvoiProvider = FutureProvider<List<EvenementEnFile>>(
  (ref) => ref.read(depotFileEnvoiProvider).lister(),
);

/// Nombre d'éléments saisis sur l'appareil et pas encore envoyés.
final nombreEnAttenteProvider = Provider<int>((ref) {
  final file = ref.watch(fileEnvoiProvider).valueOrNull ?? const [];
  return file.where((evenement) => evenement.enAttente).length;
});

/// Opérateur connecté et son rôle, ou `null` si l'accès n'est pas ouvert.
final operateurProvider =
    Provider<({ProfilUtilisateur profil, RoleTerrain role})?>((ref) {
      final etat = ref.watch(controleurAuthProvider);
      return etat is AuthDeverrouille
          ? (profil: etat.profil, role: etat.role)
          : null;
    });
