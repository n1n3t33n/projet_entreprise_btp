import '../../../core/outils/identifiants.dart';
import '../../../core/stockage/magasin_documents.dart';
import '../../auth/domain/profil_utilisateur.dart';
import '../../sync/data/depot_file_envoi.dart';
import '../domain/modeles.dart';
import 'donnees_demo.dart';

/// Levée quand une personne tente de valider sa propre opération : celui qui
/// réalise ne valide pas (séparation des fonctions, charte § 10).
class SeparationFonctionsException implements Exception {
  const SeparationFonctionsException();
}

/// Dépôt du stock sur l'appareil.
///
/// Tout est enregistré localement (base chiffrée) et chaque saisie ajoute un
/// événement à la file d'envoi : l'application fonctionne sans réseau, le
/// serveur recevra les événements à la prochaine synchronisation.
class DepotStock {
  DepotStock(this._documents, this._file, {DateTime Function()? horloge})
    : _horloge = horloge ?? DateTime.now;

  final MagasinDocuments _documents;
  final DepotFileEnvoi _file;
  final DateTime Function() _horloge;

  static const String _type = 'stock';

  Future<List<ArticleStock>> articles() async {
    final brut = await _documents.lireListe(_type, 'articles');
    if (brut != null) return brut.map(ArticleStock.fromJson).toList();
    final demo = articlesDemo(_horloge());
    await _ecrireArticles(demo);
    return demo;
  }

  /// Mouvements, du plus récent au plus ancien.
  Future<List<MouvementStock>> mouvements() async {
    final brut = await _documents.lireListe(_type, 'mouvements');
    final liste = brut != null
        ? brut.map(MouvementStock.fromJson).toList()
        : mouvementsDemo(_horloge());
    if (brut == null) await _ecrireMouvements(liste);
    return liste..sort((a, b) => b.date.compareTo(a.date));
  }

  Future<Inventaire> inventaire() async {
    final brut = await _documents.lireObjet(_type, 'inventaire');
    if (brut != null) return Inventaire.fromJson(brut);
    final demo = inventaireDemo(await articles());
    await _documents.ecrireObjet(_type, 'inventaire', demo.toJson());
    return demo;
  }

  /// Enregistre un mouvement : met à jour le stock, journalise et met en file
  /// d'envoi. Un stock peut devenir négatif : c'est signalé, jamais bloqué.
  Future<MouvementStock> enregistrer({
    required ArticleStock article,
    required TypeMouvement type,
    required SensMouvement sens,
    required num quantite,
    required ProfilUtilisateur auteur,
    String? destination,
    String? reference,
    String? motif,
    List<String> photos = const [],
  }) async {
    final maintenant = _horloge();
    final existants = await mouvements();
    final aValider =
        type == TypeMouvement.sortieLogement || type == TypeMouvement.perte;
    final mouvement = MouvementStock(
      uuid: genererUuid(),
      numero: '${_prefixe(type)}-${880 + existants.length}',
      codeArticle: article.code,
      designation: article.designation,
      unite: article.unite,
      type: type,
      sens: sens,
      quantite: quantite,
      date: maintenant,
      idAuteur: auteur.idUtilisateur,
      nomAuteur: auteur.nomComplet,
      statut: type == TypeMouvement.ajustement
          ? StatutMouvement.valide
          : (aValider ? StatutMouvement.aValider : StatutMouvement.enregistre),
      destination: destination,
      reference: reference,
      motif: motif,
    );

    await _appliquer(article.code, mouvement.quantiteSignee, maintenant);
    await _ecrireMouvements([mouvement, ...existants]);
    await _file.enfiler(
      uuid: mouvement.uuid,
      type: 'MOUVEMENT_STOCK',
      chargeUtile: {
        ...mouvement.toJson(),
        'cree_le': maintenant.toIso8601String(),
        'photos': photos,
        'resume':
            '${mouvement.numero} · ${article.designation} · '
            '${formaterQuantite(quantite, article.unite)}',
      },
    );
    return mouvement;
  }

  /// Approuve ou refuse un mouvement en attente. Un refus remet la quantité
  /// en stock. L'auteur du mouvement ne peut pas décider lui-même.
  Future<void> decider(
    String uuid, {
    required bool accepte,
    required ProfilUtilisateur validateur,
  }) async {
    final liste = await mouvements();
    final index = liste.indexWhere((m) => m.uuid == uuid);
    if (index < 0) return;
    final mouvement = liste[index];
    if (mouvement.statut != StatutMouvement.aValider) return;
    if (mouvement.idAuteur == validateur.idUtilisateur) {
      throw const SeparationFonctionsException();
    }

    final maintenant = _horloge();
    liste[index] = mouvement.avecStatut(
      accepte ? StatutMouvement.valide : StatutMouvement.rejete,
    );
    if (!accepte) {
      await _appliquer(
        mouvement.codeArticle,
        -mouvement.quantiteSignee,
        maintenant,
      );
    }
    await _ecrireMouvements(liste);
    await _file.enfiler(
      uuid: genererUuid(),
      type: 'DECISION_MOUVEMENT',
      chargeUtile: {
        'uuid_mouvement': uuid,
        'decision': accepte ? 'ACCEPTEE' : 'REFUSEE',
        'id_auteur': validateur.idUtilisateur,
        'cree_le': maintenant.toIso8601String(),
        'resume': '${mouvement.numero} · ${mouvement.designation}',
      },
    );
  }

  /// Enregistre le comptage d'une ligne d'inventaire. Un écart exige une
  /// justification (contrôlé par l'écran).
  Future<Inventaire> compter(
    String codeArticle,
    num quantite, {
    required ProfilUtilisateur compteur,
    String? justification,
  }) async {
    final inventaire = await this.inventaire();
    final suivant = inventaire.copie(
      idCompteur: compteur.idUtilisateur,
      lignes: [
        for (final ligne in inventaire.lignes)
          ligne.codeArticle == codeArticle
              ? ligne.comptee(quantite, justification)
              : ligne,
      ],
    );
    await _documents.ecrireObjet(_type, 'inventaire', suivant.toJson());
    return suivant;
  }

  /// Soumet l'inventaire compté à la validation du gestionnaire.
  Future<Inventaire> soumettreInventaire() async {
    final inventaire = await this.inventaire();
    final suivant = inventaire.copie(statut: StatutInventaire.aValider);
    await _documents.ecrireObjet(_type, 'inventaire', suivant.toJson());
    await _file.enfiler(
      uuid: genererUuid(),
      type: 'INVENTAIRE_SOUMIS',
      chargeUtile: {
        'id_inventaire': inventaire.id,
        'cree_le': _horloge().toIso8601String(),
        'resume': '${inventaire.id} · ${inventaire.zone}',
      },
    );
    return suivant;
  }

  /// Valide l'inventaire : c'est le seul chemin par lequel le stock est
  /// ajusté (charte § 10). Chaque écart devient un mouvement d'ajustement.
  Future<void> validerInventaire(ProfilUtilisateur validateur) async {
    final inventaire = await this.inventaire();
    if (inventaire.statut != StatutInventaire.aValider) return;
    if (inventaire.idCompteur == validateur.idUtilisateur) {
      throw const SeparationFonctionsException();
    }
    final stock = await articles();
    for (final ligne in inventaire.ecarts) {
      final article = stock.firstWhere((a) => a.code == ligne.codeArticle);
      await enregistrer(
        article: article,
        type: TypeMouvement.ajustement,
        sens: ligne.ecart < 0 ? SensMouvement.sortie : SensMouvement.entree,
        quantite: ligne.ecart.abs(),
        auteur: validateur,
        motif: ligne.justification,
        reference: inventaire.id,
      );
    }
    await _documents.ecrireObjet(
      _type,
      'inventaire',
      inventaire.copie(statut: StatutInventaire.valide).toJson(),
    );
  }

  Future<void> _appliquer(String code, num variation, DateTime date) async {
    final stock = await articles();
    await _ecrireArticles([
      for (final a in stock)
        a.code == code ? a.avecQuantite(a.quantite + variation, date) : a,
    ]);
  }

  Future<void> _ecrireArticles(List<ArticleStock> liste) => _documents
      .ecrireListe(_type, 'articles', [for (final a in liste) a.toJson()]);

  Future<void> _ecrireMouvements(List<MouvementStock> liste) => _documents
      .ecrireListe(_type, 'mouvements', [for (final m in liste) m.toJson()]);

  String _prefixe(TypeMouvement type) => switch (type) {
    TypeMouvement.reception => 'RC',
    TypeMouvement.sortieLogement => 'SR',
    TypeMouvement.retour => 'RT',
    TypeMouvement.perte => 'PR',
    TypeMouvement.ajustement => 'AJ',
  };
}
