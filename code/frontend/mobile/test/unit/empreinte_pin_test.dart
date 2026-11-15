import 'package:chantiersync_mobile/core/securite/empreinte_pin.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('empreinte du PIN', () {
    test('le bon PIN est vérifié', () async {
      final sel = EmpreintePin.genererSel();
      final empreinte = await EmpreintePin.hacher('4821', sel);
      expect(await EmpreintePin.verifier('4821', sel, empreinte), isTrue);
    });

    test('un mauvais PIN est rejeté', () async {
      final sel = EmpreintePin.genererSel();
      final empreinte = await EmpreintePin.hacher('4821', sel);
      expect(await EmpreintePin.verifier('0000', sel, empreinte), isFalse);
    });

    test('deux sels donnent des empreintes différentes', () async {
      final sel1 = EmpreintePin.genererSel();
      final sel2 = EmpreintePin.genererSel();
      final e1 = await EmpreintePin.hacher('4821', sel1);
      final e2 = await EmpreintePin.hacher('4821', sel2);
      expect(e1 == e2, isFalse);
    });
  });
}
