import 'dart:convert';

import 'package:drift/drift.dart';

import '../../../core/db/base_locale.dart';
import '../domain/statut_envoi.dart';

/// Événement saisi sur l'appareil, en attente d'envoi ou déjà transmis.
class EvenementEnFile {
  const EvenementEnFile({
    required this.uuid,
    required this.type,
    required this.chargeUtile,
    required this.statut,
  });

  final String uuid;

  /// Nature de l'événement (`SORTIE_STOCK`, `POINTAGE_ETAPE`…).
  final String type;
  final Map<String, dynamic> chargeUtile;
  final StatutEnvoi statut;

  /// Instant de saisie sur l'appareil, porté par la charge utile.
  DateTime get creeLe {
    final brut = chargeUtile['cree_le'];
    return brut is String
        ? DateTime.tryParse(brut) ?? DateTime(2000)
        : DateTime(2000);
  }

  /// Libellé court prêt à afficher, fourni par l'écran qui a créé l'événement.
  String get resume => chargeUtile['resume'] as String? ?? type;

  bool get enAttente =>
      statut == StatutEnvoi.enAttente || statut == StatutEnvoi.enCours;
}

/// Dépôt de la file d'envoi (ET-3).
///
/// L'enfilement est idempotent : la clé étant l'UUID d'événement, réinsérer le
/// même événement est ignoré.
abstract interface class DepotFileEnvoi {
  /// Enfile un événement. Renvoie `true` s'il a été ajouté, `false` s'il était
  /// déjà présent.
  Future<bool> enfiler({
    required String uuid,
    required String type,
    required Map<String, dynamic> chargeUtile,
  });

  /// Tous les événements, du plus récent au plus ancien.
  Future<List<EvenementEnFile>> lister();

  Future<void> marquer(String uuid, StatutEnvoi statut);
}

/// Classe les événements du plus récent au plus ancien.
List<EvenementEnFile> _trier(List<EvenementEnFile> evenements) {
  return [...evenements]..sort((a, b) => b.creeLe.compareTo(a.creeLe));
}

/// File d'envoi sur la base locale chiffrée (table `file_envoi`).
class DepotFileEnvoiDrift implements DepotFileEnvoi {
  const DepotFileEnvoiDrift(this._base);

  final BaseLocale _base;

  @override
  Future<bool> enfiler({
    required String uuid,
    required String type,
    required Map<String, dynamic> chargeUtile,
  }) async {
    final lignes = await _base
        .into(_base.fileEnvoi)
        .insert(
          FileEnvoiCompanion.insert(
            uuidEvenement: uuid,
            typeEvenement: type,
            chargeUtile: jsonEncode(chargeUtile),
            statut: StatutEnvoi.enAttente.code,
          ),
          mode: InsertMode.insertOrIgnore,
        );
    return lignes > 0;
  }

  @override
  Future<List<EvenementEnFile>> lister() async {
    final lignes = await _base.select(_base.fileEnvoi).get();
    return _trier([
      for (final ligne in lignes)
        EvenementEnFile(
          uuid: ligne.uuidEvenement,
          type: ligne.typeEvenement,
          chargeUtile: jsonDecode(ligne.chargeUtile) as Map<String, dynamic>,
          statut: StatutEnvoi.parCode(ligne.statut),
        ),
    ]);
  }

  @override
  Future<void> marquer(String uuid, StatutEnvoi statut) {
    return (_base.update(_base.fileEnvoi)
          ..where((t) => t.uuidEvenement.equals(uuid)))
        .write(FileEnvoiCompanion(statut: Value(statut.code)));
  }
}

/// File d'envoi en mémoire, pour les tests.
class DepotFileEnvoiMemoire implements DepotFileEnvoi {
  final Map<String, EvenementEnFile> _evenements = {};

  @override
  Future<bool> enfiler({
    required String uuid,
    required String type,
    required Map<String, dynamic> chargeUtile,
  }) async {
    if (_evenements.containsKey(uuid)) return false;
    _evenements[uuid] = EvenementEnFile(
      uuid: uuid,
      type: type,
      chargeUtile: chargeUtile,
      statut: StatutEnvoi.enAttente,
    );
    return true;
  }

  @override
  Future<List<EvenementEnFile>> lister() async =>
      _trier(_evenements.values.toList());

  @override
  Future<void> marquer(String uuid, StatutEnvoi statut) async {
    final existant = _evenements[uuid];
    if (existant == null) return;
    _evenements[uuid] = EvenementEnFile(
      uuid: existant.uuid,
      type: existant.type,
      chargeUtile: existant.chargeUtile,
      statut: statut,
    );
  }
}
