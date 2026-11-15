import 'package:chantiersync_mobile/features/auth/data/dto_auth.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('DTO d\'authentification (contrat web, snake_case)', () {
    final json = {
      'jeton': 'jeton-abc',
      'utilisateur': {
        'id_utilisateur': 'u-1',
        'identifiant': 'magasinier',
        'nom': 'Koné',
        'prenom': 'Awa',
        'fonction': 'Magasinière',
        'statut': 'ACTIF',
        'date_creation': '2026-01-01T00:00:00.000',
        'role_code_role': 'MAGASINIER',
        'perimetre_id_perimetre': 'perim-bassam',
        'libelle_perimetre': 'Chantier Grand-Bassam',
      },
    };

    test('désérialise la session', () {
      final session = SessionDto.fromJson(json);
      expect(session.jeton, 'jeton-abc');
      expect(session.utilisateur.roleCodeRole, 'MAGASINIER');
      expect(session.utilisateur.identifiant, 'magasinier');
    });

    test('ré-sérialise en snake_case', () {
      final session = SessionDto.fromJson(json);
      final sortie = session.toJson();
      final utilisateur = sortie['utilisateur'] as Map<String, dynamic>;
      expect(utilisateur.containsKey('role_code_role'), isTrue);
      expect(utilisateur['id_utilisateur'], 'u-1');
    });

    test('lit le motif d\'échec', () {
      final echec = EchecConnexionDto.fromJson({
        'motif': 'VERROUILLE',
        'message': 'Compte verrouillé',
        'secondes_restantes': 60,
      });
      expect(echec.motif, 'VERROUILLE');
      expect(echec.secondesRestantes, 60);
    });
  });
}
