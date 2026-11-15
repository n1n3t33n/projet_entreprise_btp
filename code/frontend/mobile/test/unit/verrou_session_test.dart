import 'package:chantiersync_mobile/features/auth/domain/verrou_session.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('verrou de session (14 jours)', () {
    final connexion = DateTime(2026, 11, 1, 8);

    test('valide le jour même', () {
      expect(verrouExpire(connexion, DateTime(2026, 11, 1, 9)), isFalse);
    });

    test('valide juste avant 14 jours', () {
      expect(verrouExpire(connexion, DateTime(2026, 11, 14, 8)), isFalse);
    });

    test('expire à 14 jours pile', () {
      expect(verrouExpire(connexion, DateTime(2026, 11, 15, 8)), isTrue);
    });

    test('expire au-delà de 14 jours', () {
      expect(verrouExpire(connexion, DateTime(2026, 12, 1, 8)), isTrue);
    });

    test('temps restant nul une fois expiré', () {
      expect(
        tempsRestantVerrou(connexion, DateTime(2026, 12, 1, 8)),
        Duration.zero,
      );
    });

    test('temps restant positif avant expiration', () {
      final restant = tempsRestantVerrou(connexion, DateTime(2026, 11, 8, 8));
      expect(restant, const Duration(days: 7));
    });
  });
}
