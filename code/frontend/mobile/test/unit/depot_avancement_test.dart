import 'package:chantiersync_mobile/core/stockage/magasin_documents.dart';
import 'package:chantiersync_mobile/features/auth/domain/profil_utilisateur.dart';
import 'package:chantiersync_mobile/features/avancement/data/depot_avancement.dart';
import 'package:chantiersync_mobile/features/avancement/data/donnees_demo.dart';
import 'package:chantiersync_mobile/features/avancement/domain/modeles.dart';
import 'package:chantiersync_mobile/features/stock/data/depot_stock.dart';
import 'package:chantiersync_mobile/features/sync/data/depot_file_envoi.dart';
import 'package:flutter_test/flutter_test.dart';

const ProfilUtilisateur technicien = ProfilUtilisateur(
  idUtilisateur: 'u-technicien',
  identifiant: 'technicien',
  prenom: 'Kouassi',
  nom: 'Adama',
  fonction: 'Technicien',
  perimetre: 'Chantier de Grand-Bassam',
);

const ProfilUtilisateur chef = ProfilUtilisateur(
  idUtilisateur: 'u-chef',
  identifiant: 'chef',
  prenom: 'Mamadou',
  nom: 'Traoré',
  fonction: 'Chef de chantier',
  perimetre: 'Chantier de Grand-Bassam',
);

void main() {
  late DepotFileEnvoiMemoire file;
  late DepotAvancement depot;
  var maintenant = DateTime(2026, 11, 14, 10);

  setUp(() {
    maintenant = DateTime(2026, 11, 14, 10);
    file = DepotFileEnvoiMemoire();
    depot = DepotAvancement(
      MagasinDocumentsMemoire(),
      file,
      horloge: () => maintenant,
    );
  });

  Future<EtapeTravaux> etape(String id) async =>
      (await depot.etapes()).firstWhere((e) => e.id == id);

  group('cycle de vie des étapes', () {
    test(
      'démarrer une étape à faire la passe en cours et lance le pointage',
      () async {
        await depot.demarrer('106', technicien);
        final apres = await etape('106');
        expect(apres.statut, StatutEtape.enCours);
        expect(apres.pointageActif, isTrue);
        expect((await file.lister()).single.type, 'EVENEMENT_ETAPE');
      },
    );

    test('on ne démarre pas une étape déjà en cours', () {
      expect(
        () => depot.demarrer('104', technicien),
        throwsA(isA<TransitionInterditeException>()),
      );
    });

    test('la pause conserve le temps pointé', () async {
      final avant = (await etape('104')).dureePointee(maintenant);
      await depot.basculerPointage('104', technicien);
      maintenant = maintenant.add(const Duration(hours: 1));
      final enPause = await etape('104');
      expect(enPause.pointageActif, isFalse);
      expect(enPause.dureePointee(maintenant), avant);
    });

    test('une étape incomplète ne peut pas être déclarée terminée', () {
      expect(
        () => depot.terminer('104', technicien),
        throwsA(isA<TransitionInterditeException>()),
      );
    });

    test(
      'métré atteint et contrôles cochés : la validation est attendue',
      () async {
        await depot.pointer(
          '104',
          metreFait: 8,
          controlesFaits: const [true, true],
          auteur: technicien,
        );
        await depot.terminer('104', technicien);
        final apres = await etape('104');
        expect(apres.statut, StatutEtape.termineeDeclaree);
        expect(apres.idAuteurDeclaration, technicien.idUtilisateur);
        expect(apres.pointageActif, isFalse);
      },
    );

    test('le métré pointé ne dépasse jamais la cible', () async {
      await depot.pointer(
        '104',
        metreFait: 99,
        controlesFaits: const [true, false],
        auteur: technicien,
      );
      expect((await etape('104')).metreFait, 8);
    });
  });

  group('validation', () {
    test('celui qui a déclaré la fin ne peut pas valider', () {
      expect(
        () => depot.decider('108', accepte: true, validateur: technicien),
        throwsA(isA<SeparationFonctionsException>()),
      );
    });

    test('un tiers valide', () async {
      await depot.decider('108', accepte: true, validateur: chef);
      expect((await etape('108')).statut, StatutEtape.validee);
    });

    test('un refus remet en cours', () async {
      await depot.decider('107', accepte: false, validateur: chef);
      expect((await etape('107')).statut, StatutEtape.enCours);
      expect((await depot.evenements()).first.type, TypeEvenement.rejet);
    });
  });

  group('blocage et réaffectation', () {
    test(
      'un blocage arrête le travail et garde la référence manquante',
      () async {
        await depot.declarerBlocage(
          '104',
          Blocage(
            nature: NatureBlocage.ruptureMateriau,
            gravite: GraviteBlocage.arretTotal,
            retard: RetardEstime.deuxHeures,
            date: maintenant,
            codeArticle: 'FER-012',
            designationArticle: 'Fer à béton HA Ø12',
          ),
          technicien,
        );
        final apres = await etape('104');
        expect(apres.statut, StatutEtape.bloquee);
        expect(apres.blocage?.codeArticle, 'FER-012');
        expect(apres.pointageActif, isFalse);
      },
    );

    test('lever un blocage sans pointage rend à faire', () async {
      await depot.leverBlocage('105', technicien);
      final apres = await etape('105');
      expect(apres.statut, StatutEtape.aFaire);
      expect(apres.blocage, isNull);
    });

    test('la réaffectation change équipe et responsable', () async {
      await depot.reaffecter(
        '105',
        equipe: equipesDemo.first,
        motif: 'Retard de planning',
        auteur: chef,
      );
      final apres = await etape('105');
      expect(apres.equipe, equipesDemo.first.nom);
      expect(apres.idResponsable, equipesDemo.first.idChef);
    });
  });
}
