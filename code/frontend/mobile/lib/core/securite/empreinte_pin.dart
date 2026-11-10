import 'dart:convert';
import 'dart:math';

import 'package:cryptography/cryptography.dart';

/// Empreinte du PIN par PBKDF2-HMAC-SHA256.
///
/// Le PIN n'est jamais stocké en clair : on garde un sel aléatoire et
/// l'empreinte dérivée. La vérification recalcule l'empreinte et compare à
/// temps constant.
abstract final class EmpreintePin {
  static const int _iterations = 120000;
  static const int _bits = 256;

  /// Sel aléatoire (16 octets) encodé en base64, à conserver avec l'empreinte.
  static String genererSel() {
    final aleatoire = Random.secure();
    final octets = List<int>.generate(16, (_) => aleatoire.nextInt(256));
    return base64Encode(octets);
  }

  /// Dérive l'empreinte base64 du [pin] avec le [selBase64] fourni.
  static Future<String> hacher(String pin, String selBase64) async {
    final algo = Pbkdf2(
      macAlgorithm: Hmac.sha256(),
      iterations: _iterations,
      bits: _bits,
    );
    final cle = await algo.deriveKey(
      secretKey: SecretKey(utf8.encode(pin)),
      nonce: base64Decode(selBase64),
    );
    final octets = await cle.extractBytes();
    return base64Encode(octets);
  }

  /// Vrai si [pin] correspond à [empreinteAttendue] pour ce [selBase64].
  static Future<bool> verifier(
    String pin,
    String selBase64,
    String empreinteAttendue,
  ) async {
    final calculee = await hacher(pin, selBase64);
    return _egaliteTempsConstant(calculee, empreinteAttendue);
  }

  static bool _egaliteTempsConstant(String a, String b) {
    if (a.length != b.length) return false;
    var difference = 0;
    for (var i = 0; i < a.length; i++) {
      difference |= a.codeUnitAt(i) ^ b.codeUnitAt(i);
    }
    return difference == 0;
  }
}
