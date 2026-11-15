import 'package:drift/drift.dart';

import '../db/base_locale.dart';
import 'magasin_documents.dart';

/// Magasin de documents adossé à la base locale chiffrée (table
/// `cache_reference`). La version de chaque document augmente à chaque
/// écriture : elle servira au téléchargement incrémental des références.
class MagasinDocumentsDrift implements MagasinDocuments {
  const MagasinDocumentsDrift(this._base);

  final BaseLocale _base;

  @override
  Future<String?> lire(String type, String cle) async {
    final ligne = await _requete(type, cle).getSingleOrNull();
    return ligne?.contenu;
  }

  @override
  Future<void> ecrire(String type, String cle, String contenu) async {
    final existante = await _requete(type, cle).getSingleOrNull();
    await _base
        .into(_base.cacheReference)
        .insertOnConflictUpdate(
          CacheReferenceCompanion.insert(
            typeDonnee: type,
            cle: cle,
            contenu: contenu,
            version: (existante?.version ?? 0) + 1,
          ),
        );
  }

  @override
  Future<void> supprimer(String type, String cle) {
    return (_base.delete(
      _base.cacheReference,
    )..where((t) => t.typeDonnee.equals(type) & t.cle.equals(cle))).go();
  }

  @override
  Future<void> vider() => _base.delete(_base.cacheReference).go();

  SimpleSelectStatement<$CacheReferenceTable, CacheReferenceRow> _requete(
    String type,
    String cle,
  ) {
    return _base.select(_base.cacheReference)
      ..where((t) => t.typeDonnee.equals(type) & t.cle.equals(cle));
  }
}
