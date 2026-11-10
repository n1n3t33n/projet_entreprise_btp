import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Coffre de l'appareil : Keystore (Android) / Keychain (iOS) via
/// flutter_secure_storage. Il garde la clé de chiffrement de la base locale et
/// le jeton de session. Rien de sensible n'est écrit ailleurs en clair.
class Coffre {
  const Coffre(this._stockage);

  final FlutterSecureStorage _stockage;

  static const _cleBase = 'cle_base';
  static const _jeton = 'jeton_session';

  Future<String?> lireCleBase() => _stockage.read(key: _cleBase);

  Future<void> ecrireCleBase(String valeur) =>
      _stockage.write(key: _cleBase, value: valeur);

  Future<String?> lireJeton() => _stockage.read(key: _jeton);

  Future<void> ecrireJeton(String valeur) =>
      _stockage.write(key: _jeton, value: valeur);

  /// Efface tout : appelé à la révocation / déconnexion (SQ-5).
  Future<void> vider() => _stockage.deleteAll();
}
