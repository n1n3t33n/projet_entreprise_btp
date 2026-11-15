import 'package:chantiersync_mobile/core/navigation/onglet_role.dart';
import 'package:chantiersync_mobile/core/outils/identifiants.dart';
import 'package:chantiersync_mobile/core/roles/role_terrain.dart';
import 'package:chantiersync_mobile/core/stockage/magasin_documents.dart';
import 'package:chantiersync_mobile/features/sync/data/depot_file_envoi.dart';
import 'package:chantiersync_mobile/features/sync/data/moteur_synchronisation.dart';
import 'package:chantiersync_mobile/features/sync/domain/statut_envoi.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('file d\'envoi', () {
    test(
      'enfiler deux fois le même événement ne crée pas de doublon',
      () async {
        final file = DepotFileEnvoiMemoire();
        final charge = {
          'cree_le': DateTime(2026, 11, 14, 10).toIso8601String(),
        };

        expect(
          await file.enfiler(
            uuid: 'a',
            type: 'SORTIE_STOCK',
            chargeUtile: charge,
          ),
          isTrue,
        );
        expect(
          await file.enfiler(
            uuid: 'a',
            type: 'SORTIE_STOCK',
            chargeUtile: charge,
          ),
          isFalse,
        );
        expect(await file.lister(), hasLength(1));
      },
    );

    test('les événements sont listés du plus récent au plus ancien', () async {
      final file = DepotFileEnvoiMemoire();
      for (final (uuid, heure) in [
        ('ancien', 8),
        ('recent', 11),
        ('milieu', 9),
      ]) {
        await file.enfiler(
          uuid: uuid,
          type: 'SORTIE_STOCK',
          chargeUtile: {
            'cree_le': DateTime(2026, 11, 14, heure).toIso8601String(),
          },
        );
      }
      expect((await file.lister()).map((e) => e.uuid), [
        'recent',
        'milieu',
        'ancien',
      ]);
    });

    test('un événement accepté n\'est plus en attente', () async {
      final file = DepotFileEnvoiMemoire();
      await file.enfiler(
        uuid: 'a',
        type: 'SORTIE_STOCK',
        chargeUtile: const {},
      );
      await file.marquer('a', StatutEnvoi.accepte);
      expect((await file.lister()).single.enAttente, isFalse);
    });
  });

  group('magasin de documents', () {
    test('relit une liste écrite, et rien pour une clé absente', () async {
      final magasin = MagasinDocumentsMemoire();
      await magasin.ecrireListe('stock', 'lignes', [
        {'code': 'CIM-045'},
      ]);
      expect(
        (await magasin.lireListe('stock', 'lignes'))?.single['code'],
        'CIM-045',
      );
      expect(await magasin.lireListe('stock', 'absent'), isNull);
    });
  });

  group('navigation par rôle', () {
    test('le premier onglet est le tableau de bord du rôle', () {
      expect(ongletsPour(RoleTerrain.magasinier).first, OngletRole.stock);
      expect(ongletsPour(RoleTerrain.technicien).first, OngletRole.fiches);
      expect(ongletsPour(RoleTerrain.chefChantier).first, OngletRole.aValider);
    });

    test('seuls les rôles qui contrôlent voient « À valider »', () {
      bool valide(RoleTerrain role) =>
          ongletsPour(role).contains(OngletRole.aValider);
      expect(valide(RoleTerrain.magasinier), isFalse);
      expect(valide(RoleTerrain.technicien), isFalse);
      expect(valide(RoleTerrain.gestionnaireStock), isTrue);
      expect(valide(RoleTerrain.chefChantier), isTrue);
      expect(valide(RoleTerrain.responsableTechnique), isTrue);
    });

    test('tout rôle garde un accès à son profil', () {
      for (final role in RoleTerrain.values) {
        expect(ongletsPour(role).last, OngletRole.profil);
        expect(ongletsPour(role).length, lessThanOrEqualTo(5));
      }
    });
  });

  group('identifiants', () {
    test('les identifiants d\'événement sont uniques et au bon format', () {
      final uuids = {for (var i = 0; i < 200; i++) genererUuid()};
      expect(uuids, hasLength(200));
      expect(
        RegExp(
          r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
        ).hasMatch(uuids.first),
        isTrue,
      );
    });

    test('les initiales reprennent le prénom et le nom', () {
      expect(initiales('Mamadou Koné'), 'MK');
      expect(initiales('  kouassi  '), 'K');
      expect(initiales(''), '?');
    });
  });
  group('synchronisation', () {
    test('synchroniser envoie la file une seule fois', () async {
      final file = DepotFileEnvoiMemoire();
      final moteur = MoteurSynchronisation(MagasinDocumentsMemoire(), file);
      await file.enfiler(
        uuid: 'a',
        type: 'MOUVEMENT_STOCK',
        chargeUtile: const {},
      );
      await file.enfiler(
        uuid: 'b',
        type: 'EVENEMENT_ETAPE',
        chargeUtile: const {},
      );

      expect(await moteur.synchroniser(), 2);
      expect((await file.lister()).every((e) => !e.enAttente), isTrue);
      expect(await moteur.synchroniser(), 0);
      expect((await moteur.etat()).derniere, isNotNull);
    });

    test('un conflit disparait une fois tranche', () async {
      final moteur = MoteurSynchronisation(
        MagasinDocumentsMemoire(),
        DepotFileEnvoiMemoire(),
      );
      final conflit = (await moteur.etat()).conflits.single;
      await moteur.resoudre(conflit.id, ResolutionConflit.prioriteServeur);
      expect((await moteur.etat()).conflits, isEmpty);
    });
  });
}
