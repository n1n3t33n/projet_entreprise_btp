import 'package:flutter/material.dart';

/// Jetons de la charte graphique Schiavone (source : cadrage/wireframes/charte.md).
///
/// Source unique de vérité du style côté mobile : couleurs, typographie,
/// rayons, espacements et durées. Aucune valeur n'est réécrite en dur ailleurs
/// dans l'application — tout passe par ces constantes, pour rester modulable et
/// cohérent avec le poste de pilotage web.
abstract final class Jetons {
  // Couleurs de marque.
  static const Color marine = Color(0xFF002E5E);
  static const Color sarcelle = Color(0xFF1F7FA8);
  static const Color or = Color(0xFF8A6508);
  static const Color orClair = Color(0xFFFBF1CF);
  static const Color orVif = Color(0xFFF6DF94);

  // Fonds.
  static const Color fond = Color(0xFFF3F8FC);
  static const Color fondSection = Color(0xFFEAF6FC);
  static const Color surface = Color(0xFFFFFFFF);

  // Texte.
  static const Color texte = Color(0xFF2B3A4A);
  static const Color texteSecondaire = Color(0xFF5A6572);
  static const Color texteAttenue = Color(0xFF9AA5B1);

  // États.
  static const Color succes = Color(0xFF2E7D32);
  static const Color danger = Color(0xFFC0392B);

  // Bordures.
  static const Color bordure = Color(0xFFE3EDF5);

  // Rayons d'angle.
  static const double rayonCarte = 16;
  static const double rayonChamp = 12;

  // Échelle d'espacement 4 / 8 / 16 / 24 / 32.
  static const double espace1 = 4;
  static const double espace2 = 8;
  static const double espace3 = 16;
  static const double espace4 = 24;
  static const double espace5 = 32;

  // Marge latérale mobile (référence 390 px).
  static const double margeMobile = 16;

  // Cible tactile minimale d'un bouton principal.
  static const double cibleTactile = 56;

  // Durées d'animation (discrètes, porteuses de sens).
  static const Duration dureeMicro = Duration(milliseconds: 160);
  static const Duration dureeNormale = Duration(milliseconds: 240);
  static const Duration dureeCascade = Duration(milliseconds: 200);
}
