// Captures des écrans du module Avancement. Voir apercus_test.dart.

import 'package:chantiersync_mobile/core/roles/role_terrain.dart';
import 'package:chantiersync_mobile/features/auth/domain/profil_utilisateur.dart';
import 'package:chantiersync_mobile/features/avancement/presentation/ecrans_etapes.dart';
import 'package:chantiersync_mobile/features/avancement/presentation/ecrans_suivi.dart';
import 'package:chantiersync_mobile/features/shell/presentation/coquille.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import '../support/aide_tests.dart';

const bool _actif = bool.fromEnvironment('APERCUS');

const ProfilUtilisateur _technicien = ProfilUtilisateur(
  idUtilisateur: 'u-technicien',
  identifiant: 'technicien',
  prenom: 'Kouassi',
  nom: 'Adama',
  fonction: 'Technicien',
  perimetre: 'Chantier de Grand-Bassam',
);

const ProfilUtilisateur _chef = ProfilUtilisateur(
  idUtilisateur: 'u-chef',
  identifiant: 'chef',
  prenom: 'Mamadou',
  nom: 'Traoré',
  fonction: 'Chef de chantier',
  perimetre: 'Chantier de Grand-Bassam',
);

void main() {
  setUpAll(() async {
    TestWidgetsFlutterBinding.ensureInitialized();
    await chargerPolices();
  });

  Future<void> apercu(
    WidgetTester tester,
    String nom,
    Widget ecran, {
    required RoleTerrain role,
    required ProfilUtilisateur profil,
    double hauteur = 1600,
  }) async {
    debugDisableShadows = false;
    definirEcran(tester, hauteur: hauteur);
    await tester.pumpWidget(
      monter(ecran, overrides: doublures(etat: etatOuvert(role, profil))),
    );
    await tester.pumpAndSettle();
    await capturer(tester, nom);
    debugDisableShadows = true;
  }

  testWidgets('accueil technicien', skip: !_actif, (tester) async {
    await apercu(
      tester,
      'a2_technicien',
      const Coquille(profil: _technicien, role: RoleTerrain.technicien),
      role: RoleTerrain.technicien,
      profil: _technicien,
      hauteur: 1900,
    );
  });

  testWidgets('accueil chef', skip: !_actif, (tester) async {
    await apercu(
      tester,
      'a3_chef',
      const Coquille(profil: _chef, role: RoleTerrain.chefChantier),
      role: RoleTerrain.chefChantier,
      profil: _chef,
    );
  });

  testWidgets('accueil responsable', skip: !_actif, (tester) async {
    await apercu(
      tester,
      'a5_responsable',
      const Coquille(profil: _chef, role: RoleTerrain.responsableTechnique),
      role: RoleTerrain.responsableTechnique,
      profil: _chef,
    );
  });

  testWidgets('pointage', skip: !_actif, (tester) async {
    await apercu(
      tester,
      'e12_etape',
      const EcranEtape(id: '104'),
      role: RoleTerrain.technicien,
      profil: _technicien,
    );
  });

  testWidgets('blocage', skip: !_actif, (tester) async {
    await apercu(
      tester,
      'e13_blocage',
      const EcranBlocage(idEtape: '104'),
      role: RoleTerrain.technicien,
      profil: _technicien,
    );
  });

  testWidgets('controles', skip: !_actif, (tester) async {
    await apercu(
      tester,
      'e14_controles',
      const EcranControles(),
      role: RoleTerrain.chefChantier,
      profil: _chef,
    );
  });

  testWidgets('reaffectation', skip: !_actif, (tester) async {
    await apercu(
      tester,
      'e15_reaffectation',
      const EcranReaffectation(idEtape: '105'),
      role: RoleTerrain.chefChantier,
      profil: _chef,
    );
  });

  testWidgets('journal', skip: !_actif, (tester) async {
    await apercu(
      tester,
      'e16_journal',
      const EcranJournalEtape(idEtape: '104'),
      role: RoleTerrain.chefChantier,
      profil: _chef,
      hauteur: 1200,
    );
  });
}
