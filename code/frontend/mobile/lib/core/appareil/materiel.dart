import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:image_picker/image_picker.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';

import '../../components/en_tetes.dart';
import '../../theme/jetons.dart';
import '../../theme/palette.dart';

// Accès au matériel de l'appareil : caméra (lecture de code-barres, photo
// justificative) et partage de fichier. Chaque fonction rend `null` ou
// `false` si le matériel est indisponible ou refusé : l'écran appelant
// l'annonce à l'opérateur, sans jamais bloquer la saisie.

/// Ouvre la caméra pour lire un code-barres. Rend le code lu, ou `null` si
/// l'opérateur revient en arrière.
Future<String?> scannerCode(BuildContext context) {
  return Navigator.of(
    context,
  ).push<String>(MaterialPageRoute(builder: (_) => const _EcranScan()));
}

/// Prend une photo justificative. Rend son chemin sur l'appareil, ou `null`
/// si la prise de vue est annulée ou impossible.
Future<String?> prendrePhoto() async {
  try {
    final photo = await ImagePicker().pickImage(
      source: ImageSource.camera,
      maxWidth: 1600,
      imageQuality: 72,
    );
    return photo?.path;
  } on PlatformException {
    return null;
  } on MissingPluginException {
    return null;
  }
}

/// Enregistre un contenu CSV dans un fichier temporaire et ouvre le partage
/// du système. Rend `false` si le partage est impossible.
Future<bool> partagerCsv({
  required String nomFichier,
  required String contenu,
}) async {
  try {
    final dossier = await getTemporaryDirectory();
    final fichier = File(p.join(dossier.path, nomFichier));
    // Le marqueur d'ordre des octets fait reconnaître les accents aux tableurs.
    await fichier.writeAsString('﻿$contenu');
    await SharePlus.instance.share(ShareParams(files: [XFile(fichier.path)]));
    return true;
  } on PlatformException {
    return false;
  } on MissingPluginException {
    return false;
  } on FileSystemException {
    return false;
  }
}

/// Protège une valeur pour une cellule CSV (séparateur point-virgule).
String celluleCsv(Object? valeur) {
  final texte = '${valeur ?? ''}';
  return texte.contains(RegExp('[;"\n]'))
      ? '"${texte.replaceAll('"', '""')}"'
      : texte;
}

class _EcranScan extends StatefulWidget {
  const _EcranScan();

  @override
  State<_EcranScan> createState() => _EcranScanState();
}

class _EcranScanState extends State<_EcranScan> {
  bool _lu = false;

  void _detecter(BarcodeCapture capture) {
    if (_lu) return;
    final code = capture.barcodes.map((b) => b.rawValue).nonNulls.firstOrNull;
    if (code == null) return;
    _lu = true;
    HapticFeedback.mediumImpact();
    Navigator.of(context).pop(code);
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    return Scaffold(
      appBar: BarreEcran(titre: t.scanTitre, sousTitre: t.scanAide),
      body: Stack(
        fit: StackFit.expand,
        children: [
          MobileScanner(
            onDetect: _detecter,
            errorBuilder: (context, erreur) => Center(
              child: Padding(
                padding: const EdgeInsets.all(Jetons.espace4),
                child: Text(
                  t.scanIndisponible,
                  textAlign: TextAlign.center,
                  style: TextStyle(color: context.palette.texteSecondaire),
                ),
              ),
            ),
          ),
          // Cadre de visée : montre où présenter le code.
          Center(
            child: Container(
              width: 260,
              height: 150,
              decoration: BoxDecoration(
                border: Border.all(color: Colors.white, width: 3),
                borderRadius: BorderRadius.circular(Jetons.rayonBloc),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
