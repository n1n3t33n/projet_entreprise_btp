import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Coffre de l'appareil : Keystore (Android) / Keychain (iOS) via
/// flutter_secure_storage. Il garde la clé de chiffrement de la base locale,
/// le jeton de session et quelques réglages de l'appareil. Rien de sensible
/// n'est écrit ailleurs en clair.
class Coffre {
  const Coffre(this._stockage);

  final FlutterSecureStorage _stockage;

  static const _cleBase = 'cle_base';
  static const _jeton = 'jeton_session';
  static const _idAppareil = 'id_appareil';

  Future<String?> lireCleBase() => _stockage.read(key: _cleBase);

  Future<void> ecrireCleBase(String valeur) =>
      _stockage.write(key: _cleBase, value: valeur);

  Future<String?> lireJeton() => _stockage.read(key: _jeton);

  Future<void> ecrireJeton(String valeur) =>
      _stockage.write(key: _jeton, value: valeur);

  /// Efface le jeton de session (révocation / retrait du compte, SQ-5). La
  /// clé de la base n'est jamais effacée : sans elle, le fichier chiffré
  /// existant ne pourrait plus être rouvert.
  Future<void> effacerJeton() => _stockage.delete(key: _jeton);

  Future<String?> lireIdAppareil() => _stockage.read(key: _idAppareil);

  Future<void> ecrireIdAppareil(String valeur) =>
      _stockage.write(key: _idAppareil, value: valeur);

  /// Réglage d'affichage (langue, thème) : non sensible, mais rangé ici pour
  /// survivre à l'effacement des données métier.
  Future<String?> lireReglage(String nom) =>
      _stockage.read(key: 'reglage_$nom');

  Future<void> ecrireReglage(String nom, String valeur) =>
      _stockage.write(key: 'reglage_$nom', value: valeur);
}
