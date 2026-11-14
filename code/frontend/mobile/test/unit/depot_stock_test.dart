import 'package:chantiersync_mobile/core/stockage/magasin_documents.dart';
import 'package:chantiersync_mobile/features/auth/domain/profil_utilisateur.dart';
import 'package:chantiersync_mobile/features/stock/data/depot_stock.dart';
import 'package:chantiersync_mobile/features/stock/domain/modeles.dart';
import 'package:chantiersync_mobile/features/sync/data/depot_file_envoi.dart';
import 'package:flutter_test/flutter_test.dart';

import '../support/aide_tests.dart';

const ProfilUtilisateur gestionnaire = ProfilUtilisateur(
  idUtilisateur: 'u-gestionnaire',
  identifiant: 'gestionnaire',
  prenom: 'Idriss',
  nom: 'Sékou',
  fonction: 'Gestionnaire de stock',
  perimetre: 'Chantier de Grand-Bassam',
);

void main() {
  late DepotFileEnvoiMemoire file;
  late DepotStock depot;

  setUp(() {
    file = DepotFileEnvoiMemoire();
    depot = DepotStock(MagasinDocumentsMemoire(), file);
  });

  Future<ArticleStock> article(String code) async =>
      (await depot.articles()).firstWhere((a) => a.code == code);

  group('niveaux de stock', () {
    ArticleStock avec(num quantite) => ArticleStock(
      code: 'X',
      designation: 'X',
      famille: 'X',
      unite: 'u',
      quantite: quantite,
      seuilMinimal: 50,
      seuilCritique: 20,
      capacite: 200,
      emplacement: '',
      codeBarre: '',
      majLe: DateTime(2026),
    );

    test('le niveau suit les seuils, comme sur le poste de pilotage', () {
      expect(avec(0).niveau, NiveauStock.vide);
      expect(avec(19).niveau, NiveauStock.critique);
      expect(avec(20).niveau, NiveauStock.mini);
      expect(avec(49).niveau, NiveauStock.mini);
      expect(avec(50).niveau, NiveauStock.plein);
    });

    test('un stock négatif est classé vide et signalé', () {
      expect(avec(-3).niveau, NiveauStock.vide);
      expect(avec(-3).estNegatif, isTrue);
      expect(avec(0).estNegatif, isFalse);
    });
  });

  group('mouvements', () {
    test(
      'une sortie diminue le stock, attend une validation et part en file',
      () async {
        final ciment = await article('CIM-045');
        final mouvement = await depot.enregistrer(
          article: ciment,
          type: TypeMouvement.sortieLogement,
          sens: SensMouvement.sortie,
          quantite: 5,
          auteur: profilMagasinier,
          destination: 'Îlot B · Logement B2',
        );

        expect((await article('CIM-045')).quantite, ciment.quantite - 5);
        expect(mouvement.statut, StatutMouvement.aValider);
        expect((await depot.mouvements()).first.uuid, mouvement.uuid);
        final evenement = (await file.lister()).single;
        expect(evenement.type, 'MOUVEMENT_STOCK');
        expect(evenement.enAttente, isTrue);
      },
    );

    test('une réception augmente le stock sans validation', () async {
      final fer = await article('FER-012');
      final mouvement = await depot.enregistrer(
        article: fer,
        type: TypeMouvement.reception,
        sens: SensMouvement.entree,
        quantite: 150,
        auteur: profilMagasinier,
        reference: 'BL-2026-0600',
      );
      expect((await article('FER-012')).quantite, fer.quantite + 150);
      expect(mouvement.statut, StatutMouvement.enregistre);
    });

    test(
      'une sortie supérieure au stock est acceptée et rend le stock négatif',
      () async {
        final sable = await article('SAB-002');
        await depot.enregistrer(
          article: sable,
          type: TypeMouvement.sortieLogement,
          sens: SensMouvement.sortie,
          quantite: sable.quantite + 2,
          auteur: profilMagasinier,
        );
        expect((await article('SAB-002')).estNegatif, isTrue);
      },
    );
  });

  group('validation des sorties', () {
    Future<MouvementStock> sortieDuMagasinier() async => depot.enregistrer(
      article: await article('CIM-045'),
      type: TypeMouvement.sortieLogement,
      sens: SensMouvement.sortie,
      quantite: 4,
      auteur: profilMagasinier,
    );

    test('celui qui a saisi la sortie ne peut pas la valider', () async {
      final sortie = await sortieDuMagasinier();
      expect(
        () => depot.decider(
          sortie.uuid,
          accepte: true,
          validateur: profilMagasinier,
        ),
        throwsA(isA<SeparationFonctionsException>()),
      );
    });

    test('une autre personne peut approuver', () async {
      final sortie = await sortieDuMagasinier();
      await depot.decider(sortie.uuid, accepte: true, validateur: gestionnaire);
      final apres = (await depot.mouvements()).firstWhere(
        (m) => m.uuid == sortie.uuid,
      );
      expect(apres.statut, StatutMouvement.valide);
    });

    test('un refus remet la quantité en stock', () async {
      final avant = (await article('CIM-045')).quantite;
      final sortie = await sortieDuMagasinier();
      await depot.decider(
        sortie.uuid,
        accepte: false,
        validateur: gestionnaire,
      );
      expect((await article('CIM-045')).quantite, avant);
      final apres = (await depot.mouvements()).firstWhere(
        (m) => m.uuid == sortie.uuid,
      );
      expect(apres.statut, StatutMouvement.rejete);
    });
  });

  group('inventaire tournant', () {
    test(
      'le stock ne change pas tant que l\'inventaire n\'est pas validé',
      () async {
        final avant = (await article('FER-012')).quantite;
        await depot.compter(
          'FER-012',
          avant - 3,
          compteur: profilMagasinier,
          justification: 'Chutes de coupe',
        );
        await depot.soumettreInventaire();
        expect((await article('FER-012')).quantite, avant);
      },
    );

    test(
      'la validation ajuste le stock par un mouvement d\'ajustement',
      () async {
        final avant = (await article('FER-012')).quantite;
        await depot.compter(
          'FER-012',
          avant - 3,
          compteur: profilMagasinier,
          justification: 'Chutes de coupe',
        );
        await depot.soumettreInventaire();
        await depot.validerInventaire(gestionnaire);

        expect((await article('FER-012')).quantite, avant - 3);
        expect((await depot.inventaire()).statut, StatutInventaire.valide);
        final ajustement = (await depot.mouvements()).first;
        expect(ajustement.type, TypeMouvement.ajustement);
        expect(ajustement.motif, 'Chutes de coupe');
      },
    );

    test('celui qui a compté ne peut pas valider ses écarts', () async {
      await depot.compter(
        'FER-012',
        1,
        compteur: profilMagasinier,
        justification: 'x',
      );
      await depot.soumettreInventaire();
      expect(
        () => depot.validerInventaire(profilMagasinier),
        throwsA(isA<SeparationFonctionsException>()),
      );
    });
  });
}
