import 'dart:convert';

/// Magasin de documents de l'appareil : des contenus JSON rangés par type et
/// par clé (table `cache_reference` du modèle local, MPD-6).
///
/// Les dépôts métier (stock, avancement, synchronisation) ne connaissent que ce
/// contrat. En production il repose sur la base chiffrée ; en test, sur une
/// simple mémoire — la logique métier se vérifie donc sans base de données.
abstract interface class MagasinDocuments {
  Future<String?> lire(String type, String cle);

  Future<void> ecrire(String type, String cle, String contenu);

  Future<void> supprimer(String type, String cle);

  /// Efface tous les documents (révocation de l'appareil, SQ-5).
  Future<void> vider();
}

/// Lecture et écriture de documents déjà décodés.
extension DocumentsJson on MagasinDocuments {
  /// Lit une liste d'objets ; `null` si le document n'existe pas encore.
  Future<List<Map<String, dynamic>>?> lireListe(String type, String cle) async {
    final brut = await lire(type, cle);
    if (brut == null) return null;
    final decode = jsonDecode(brut) as List<dynamic>;
    return decode.cast<Map<String, dynamic>>();
  }

  Future<void> ecrireListe(
    String type,
    String cle,
    List<Map<String, dynamic>> elements,
  ) {
    return ecrire(type, cle, jsonEncode(elements));
  }

  Future<Map<String, dynamic>?> lireObjet(String type, String cle) async {
    final brut = await lire(type, cle);
    if (brut == null) return null;
    return jsonDecode(brut) as Map<String, dynamic>;
  }

  Future<void> ecrireObjet(
    String type,
    String cle,
    Map<String, dynamic> objet,
  ) {
    return ecrire(type, cle, jsonEncode(objet));
  }
}

/// Magasin en mémoire : pour les tests et les aperçus, sans persistance.
class MagasinDocumentsMemoire implements MagasinDocuments {
  final Map<String, String> _contenus = {};

  String _id(String type, String cle) => '$type/$cle';

  @override
  Future<String?> lire(String type, String cle) async =>
      _contenus[_id(type, cle)];

  @override
  Future<void> ecrire(String type, String cle, String contenu) async {
    _contenus[_id(type, cle)] = contenu;
  }

  @override
  Future<void> supprimer(String type, String cle) async {
    _contenus.remove(_id(type, cle));
  }

  @override
  Future<void> vider() async => _contenus.clear();
}
