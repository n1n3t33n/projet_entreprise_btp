import 'dart:math';

/// Génère un identifiant unique (UUID version 4) pour un événement saisi sur
/// l'appareil. C'est cette clé qui rend l'envoi idempotent (ET-3) : rejouer le
/// même événement ne crée jamais de doublon côté serveur.
String genererUuid() {
  final aleatoire = Random.secure();
  final octets = List<int>.generate(16, (_) => aleatoire.nextInt(256));
  octets[6] = (octets[6] & 0x0f) | 0x40;
  octets[8] = (octets[8] & 0x3f) | 0x80;
  final hexa = octets.map((o) => o.toRadixString(16).padLeft(2, '0')).join();
  return '${hexa.substring(0, 8)}-${hexa.substring(8, 12)}-'
      '${hexa.substring(12, 16)}-${hexa.substring(16, 20)}-'
      '${hexa.substring(20)}';
}

/// Identifiant court d'appareil, affiché à l'utilisateur (ex. « T-841 »).
String genererIdAppareil() => 'T-${100 + Random.secure().nextInt(900)}';

/// Initiales d'une personne : « Mamadou Koné » → « MK ».
String initiales(String nomComplet) {
  final mots = nomComplet
      .trim()
      .split(RegExp(r'\s+'))
      .where((mot) => mot.isNotEmpty)
      .toList();
  if (mots.isEmpty) return '?';
  if (mots.length == 1) return mots.first.substring(0, 1).toUpperCase();
  return (mots.first.substring(0, 1) + mots.last.substring(0, 1)).toUpperCase();
}
