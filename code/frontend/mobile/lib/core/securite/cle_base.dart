import 'dart:convert';
import 'dart:math';

/// Génère une clé aléatoire forte (32 octets) pour chiffrer la base locale.
///
/// La clé est produite une seule fois par appareil, puis conservée dans le
/// coffre matériel. Elle n'est jamais dérivée du PIN (trop court) : le PIN sert
/// à débloquer l'accès, la clé protège les données au repos.
String genererCleBase() {
  final aleatoire = Random.secure();
  final octets = List<int>.generate(32, (_) => aleatoire.nextInt(256));
  return base64UrlEncode(octets);
}
