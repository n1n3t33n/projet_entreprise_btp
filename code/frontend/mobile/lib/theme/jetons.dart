import 'package:flutter/material.dart';

/// Jetons de la charte graphique Schiavone (source : cadrage/wireframes/charte.md).
///
/// Source unique de vérité des valeurs fixes du style : couleurs de marque,
/// rayons, espacements, durées. Les couleurs qui changent selon le thème
/// (clair / sombre) ne sont pas ici : elles passent par la `Palette`
/// (voir `palette.dart`), que les écrans lisent via `context.palette`.
abstract final class Jetons {
  // Couleurs de marque (identiques dans les deux thèmes).
  static const Color marine = Color(0xFF002E5E);
  static const Color marineProfond = Color(0xFF001F42);
  static const Color sarcelle = Color(0xFF1F7FA8);
  static const Color or = Color(0xFF8A6508);
  static const Color orClair = Color(0xFFFBF1CF);
  static const Color orVif = Color(0xFFF6DF94);

  /// Cyan et sable de l'emblème Schiavone : accents réservés aux fonds sombres.
  static const Color ciel = Color(0xFF4EC9E1);
  static const Color sable = Color(0xFFF0D98C);

  // Rayons d'angle : formes généreuses, hiérarchisées (carte > bloc > contrôle).
  static const double rayonCarte = 24;
  static const double rayonBloc = 20;
  static const double rayonChamp = 16;
  static const double rayonPilule = 999;

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

  /// Décalage entre deux éléments d'une révélation en cascade.
  static const Duration pasCascade = Duration(milliseconds: 50);

  /// Courbe d'entrée commune au web et au mobile : décélère à l'arrivée.
  static const Curve courbe = Cubic(0.16, 1, 0.3, 1);

  /// Famille de police embarquée (assets/fonts).
  static const String police = 'PlusJakartaSans';
}
