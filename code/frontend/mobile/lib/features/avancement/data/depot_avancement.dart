import '../../../core/outils/identifiants.dart';
import '../../../core/stockage/magasin_documents.dart';
import '../../auth/domain/profil_utilisateur.dart';
import '../../stock/data/depot_stock.dart';
import '../../sync/data/depot_file_envoi.dart';
import '../domain/modeles.dart';
import 'donnees_demo.dart';

/// Levée quand une transition d'étape n'est pas permise (ET-1) : par exemple
/// terminer une étape dont le métré ou les contrôles ne sont pas complets.
class TransitionInterditeException implements Exception {
  const TransitionInterditeException();
}

/// Dépôt de l'avancement sur l'appareil : étapes, journal d'exécution et
/// transitions de statut (ET-1). Chaque action est journalisée et mise en
/// file d'envoi.
class DepotAvancement {
  DepotAvancement(this._documents, this._file, {DateTime Function()? horloge})
    : _horloge = horloge ?? DateTime.now;

  final MagasinDocuments _documents;
  final DepotFileEnvoi _file;
  final DateTime Function() _horloge;

  static const String _type = 'avancement';

  Future<List<EtapeTravaux>> etapes() async {
    final brut = await _documents.lireListe(_type, 'etapes');
    if (brut != null) return brut.map(EtapeTravaux.fromJson).toList();
    final demo = etapesDemo(_horloge());
    await _ecrireEtapes(demo);
    return demo;
  }

  /// Journal d'exécution, du plus récent au plus ancien.
  Future<List<EvenementEtape>> evenements() async {
    final brut = await _documents.lireListe(_type, 'evenements');
    final liste = brut != null
        ? brut.map(EvenementEtape.fromJson).toList()
        : evenementsDemo(_horloge());
    if (brut == null) await _ecrireEvenements(liste);
    return liste..sort((a, b) => b.date.compareTo(a.date));
  }

  Future<EtapeTravaux> _etape(String id) async =>
      (await etapes()).firstWhere((e) => e.id == id);

  /// Démarre une étape à faire : elle passe en cours et le pointage commence.
  Future<void> demarrer(String id, ProfilUtilisateur auteur) async {
    final etape = await _etape(id);
    if (etape.statut != StatutEtape.aFaire) {
      throw const TransitionInterditeException();
    }
    await _appliquer(
      etape.copie(statut: StatutEtape.enCours, debutPointage: _horloge()),
      TypeEvenement.demarrage,
      auteur,
    );
  }

  /// Met le pointage en pause ou le reprend. Le temps écoulé est conservé.
  Future<void> basculerPointage(String id, ProfilUtilisateur auteur) async {
    final etape = await _etape(id);
    if (etape.statut != StatutEtape.enCours) {
      throw const TransitionInterditeException();
    }
    final maintenant = _horloge();
    if (etape.pointageActif) {
      await _appliquer(
        etape.copie(
          secondesPointees: etape.dureePointee(maintenant).inSeconds,
          arreterPointage: true,
        ),
        TypeEvenement.pause,
        auteur,
      );
    } else {
      await _appliquer(
        etape.copie(debutPointage: maintenant),
        TypeEvenement.reprise,
        auteur,
      );
    }
  }

  /// Enregistre l'avancement du métré et l'état des contrôles de la gamme.
  Future<void> pointer(
    String id, {
    required num metreFait,
    required List<bool> controlesFaits,
    required ProfilUtilisateur auteur,
  }) async {
    final etape = await _etape(id);
    if (etape.statut != StatutEtape.enCours) {
      throw const TransitionInterditeException();
    }
    final borne = metreFait.clamp(0, etape.metreCible);
    await _appliquer(
      etape.copie(metreFait: borne, controlesFaits: controlesFaits),
      TypeEvenement.pointage,
      auteur,
      detail: '$borne / ${etape.metreCible} ${etape.uniteMetre}',
    );
  }

  /// Déclare l'étape terminée. Elle attend alors la validation d'un tiers.
  Future<void> terminer(String id, ProfilUtilisateur auteur) async {
    final etape = await _etape(id);
    if (etape.statut != StatutEtape.enCours || !etape.peutEtreTerminee) {
      throw const TransitionInterditeException();
    }
    await _appliquer(
      etape.copie(
        statut: etape.controleRequis
            ? StatutEtape.termineeDeclaree
            : StatutEtape.validee,
        secondesPointees: etape.dureePointee(_horloge()).inSeconds,
        arreterPointage: true,
        idAuteurDeclaration: auteur.idUtilisateur,
        nomAuteurDeclaration: auteur.nomComplet,
      ),
      TypeEvenement.fin,
      auteur,
      detail: '${etape.metreFait} / ${etape.metreCible} ${etape.uniteMetre}',
    );
  }

  /// Signale un blocage : l'étape s'arrête et l'alerte part vers le bureau.
  Future<void> declarerBlocage(
    String id,
    Blocage blocage,
    ProfilUtilisateur auteur,
  ) async {
    final etape = await _etape(id);
    if (etape.statut == StatutEtape.validee ||
        etape.statut == StatutEtape.termineeDeclaree) {
      throw const TransitionInterditeException();
    }
    await _appliquer(
      etape.copie(
        statut: StatutEtape.bloquee,
        blocage: blocage,
        secondesPointees: etape.dureePointee(_horloge()).inSeconds,
        arreterPointage: true,
      ),
      TypeEvenement.blocage,
      auteur,
      detail: blocage.designationArticle ?? blocage.observations,
    );
  }

  /// Lève un blocage : l'étape reprend là où elle s'était arrêtée.
  Future<void> leverBlocage(String id, ProfilUtilisateur auteur) async {
    final etape = await _etape(id);
    if (etape.statut != StatutEtape.bloquee) {
      throw const TransitionInterditeException();
    }
    await _appliquer(
      etape.copie(
        statut: etape.metreFait > 0 ? StatutEtape.enCours : StatutEtape.aFaire,
        leverBlocage: true,
      ),
      TypeEvenement.leveeBlocage,
      auteur,
    );
  }

  /// Valide ou refuse une étape déclarée terminée. Celui qui l'a déclarée ne
  /// peut pas la valider ; un refus la remet en cours.
  Future<void> decider(
    String id, {
    required bool accepte,
    required ProfilUtilisateur validateur,
    String? observation,
  }) async {
    final etape = await _etape(id);
    if (etape.statut != StatutEtape.termineeDeclaree) {
      throw const TransitionInterditeException();
    }
    if (etape.idAuteurDeclaration == validateur.idUtilisateur) {
      throw const SeparationFonctionsException();
    }
    await _appliquer(
      etape.copie(statut: accepte ? StatutEtape.validee : StatutEtape.enCours),
      accepte ? TypeEvenement.validation : TypeEvenement.rejet,
      validateur,
      detail: observation,
    );
  }

  /// Confie l'étape à une autre équipe, avec une consigne de transmission.
  Future<void> reaffecter(
    String id, {
    required Equipe equipe,
    required String motif,
    required ProfilUtilisateur auteur,
    String? consigne,
  }) async {
    final etape = await _etape(id);
    if (etape.statut == StatutEtape.validee) {
      throw const TransitionInterditeException();
    }
    await _appliquer(
      etape.copie(
        equipe: equipe.nom,
        idResponsable: equipe.idChef,
        nomResponsable: equipe.nomChef,
      ),
      TypeEvenement.reaffectation,
      auteur,
      detail: [
        equipe.nom,
        motif,
        if (consigne != null && consigne.isNotEmpty) consigne,
      ].join(' · '),
    );
  }

  Future<void> _appliquer(
    EtapeTravaux etape,
    TypeEvenement type,
    ProfilUtilisateur auteur, {
    String? detail,
  }) async {
    final maintenant = _horloge();
    final toutes = await etapes();
    await _ecrireEtapes([for (final e in toutes) e.id == etape.id ? etape : e]);
    final evenement = EvenementEtape(
      uuid: genererUuid(),
      idEtape: etape.id,
      libelleEtape: etape.libelle,
      type: type,
      date: maintenant,
      nomAuteur: auteur.nomComplet,
      detail: detail,
    );
    await _ecrireEvenements([evenement, ...await evenements()]);
    await _file.enfiler(
      uuid: evenement.uuid,
      type: 'EVENEMENT_ETAPE',
      chargeUtile: {
        ...evenement.toJson(),
        'statut_apres': etape.statut.code,
        'cree_le': maintenant.toIso8601String(),
        'resume': '${etape.id} · ${etape.libelle}',
      },
    );
  }

  Future<void> _ecrireEtapes(List<EtapeTravaux> liste) => _documents
      .ecrireListe(_type, 'etapes', [for (final e in liste) e.toJson()]);

  Future<void> _ecrireEvenements(List<EvenementEtape> liste) => _documents
      .ecrireListe(_type, 'evenements', [for (final e in liste) e.toJson()]);
}
