import 'package:chantiersync_mobile/features/sync/domain/statut_envoi.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('statut de la file d\'envoi', () {
    test('retrouve un statut par son code', () {
      expect(StatutEnvoi.parCode('DEJA_RECU'), StatutEnvoi.dejaRecu);
      expect(StatutEnvoi.parCode('ACCEPTE'), StatutEnvoi.accepte);
    });

    test('code inconnu retombe sur EN_ATTENTE', () {
      expect(StatutEnvoi.parCode('???'), StatutEnvoi.enAttente);
    });
  });
}
