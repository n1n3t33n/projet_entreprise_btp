import 'package:chantiersync_mobile/core/providers.dart';
import 'package:chantiersync_mobile/core/roles/role_terrain.dart';
import 'package:chantiersync_mobile/core/securite/empreinte_pin.dart';
import 'package:chantiersync_mobile/features/auth/application/controleur_auth.dart';
import 'package:chantiersync_mobile/features/auth/data/depot_session.dart';
import 'package:chantiersync_mobile/features/auth/domain/etat_auth.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_test/flutter_test.dart';

import '../support/aide_tests.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  late DepotSessionMemoire depot;
  late ProviderContainer conteneur;

  setUp(() {
    FlutterSecureStorage.setMockInitialValues({});
    depot = DepotSessionMemoire();
    conteneur = ProviderContainer(overrides: doublures(session: depot));
    addTearDown(conteneur.dispose);
  });

  EtatAuth etat() => conteneur.read(controleurAuthProvider);
  ControleurAuth controleur() =>
      conteneur.read(controleurAuthProvider.notifier);

  Future<void> enregistrerSession({required DateTime derniereConnexion}) async {
    final sel = EmpreintePin.genererSel();
    await depot.enregistrer(
      SessionEnregistree(
        profil: profilMagasinier,
        roleCode: 'MAGASINIER',
        pinHashLocal: await EmpreintePin.hacher('123456', sel),
        pinSel: sel,
        derniereConnexionEnLigne: derniereConnexion,
      ),
    );
  }

  group('parcours d\'authentification', () {
    test('sans session locale, la connexion en ligne est demandée', () async {
      await controleur().initialiser();
      expect(etat(), isA<AuthNonConnecte>());
    });

    test('connexion puis définition du code ouvrent l\'accès', () async {
      await controleur().connexionEnLigne('magasinier', 'demo');
      expect(etat(), isA<AuthEnrolementPin>());

      await controleur().definirPin('123456');
      final ouvert = etat() as AuthDeverrouille;
      expect(ouvert.role, RoleTerrain.magasinier);
      expect(ouvert.profil.nomComplet, 'Mamadou Koné');
      expect((await depot.lire())?.profil.identifiant, 'magasinier');
    });

    test('un identifiant inconnu est refusé avec le bon motif', () async {
      await controleur().connexionEnLigne('inconnu', 'demo');
      expect((etat() as AuthNonConnecte).motif, MotifConnexion.identifiants);
    });

    test('le bon code déverrouille, un mauvais code non', () async {
      await enregistrerSession(derniereConnexion: DateTime.now());
      await controleur().initialiser();
      expect(etat(), isA<AuthVerrouille>());

      expect(await controleur().deverrouiller('000000'), isFalse);
      expect(etat(), isA<AuthVerrouille>());

      expect(await controleur().deverrouiller('123456'), isTrue);
      expect(etat(), isA<AuthDeverrouille>());
    });

    test('au-delà de 14 jours, la reconnexion en ligne est exigée', () async {
      await enregistrerSession(
        derniereConnexion: DateTime.now().subtract(const Duration(days: 15)),
      );
      await controleur().initialiser();
      expect((etat() as AuthNonConnecte).motif, MotifConnexion.sessionExpiree);
    });

    test('la signature par code vérifie le PIN sans changer l\'état', () async {
      await enregistrerSession(derniereConnexion: DateTime.now());
      await controleur().initialiser();
      expect(await controleur().verifierPin('123456'), isTrue);
      expect(await controleur().verifierPin('654321'), isFalse);
      expect(etat(), isA<AuthVerrouille>());
    });

    test('retirer le compte efface la session de l\'appareil', () async {
      await enregistrerSession(derniereConnexion: DateTime.now());
      await controleur().initialiser();
      await controleur().deverrouiller('123456');

      await controleur().revoquer();
      expect((etat() as AuthNonConnecte).motif, MotifConnexion.sessionRevoquee);
      expect(await depot.lire(), isNull);
    });
  });
}
