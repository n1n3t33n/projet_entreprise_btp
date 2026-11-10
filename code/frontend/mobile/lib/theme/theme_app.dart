import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import 'jetons.dart';

/// Construit le thème Material 3 de ChantierSync à partir des [Jetons].
///
/// Police : Plus Jakarta Sans (charte). Pour le socle M1, elle est fournie par
/// `google_fonts`. En production hors-ligne, elle devra être embarquée en asset
/// `.ttf` (voir _handoff/decisions.md).
abstract final class ThemeApp {
  static ThemeData clair() {
    const schema = ColorScheme(
      brightness: Brightness.light,
      primary: Jetons.marine,
      onPrimary: Colors.white,
      secondary: Jetons.sarcelle,
      onSecondary: Colors.white,
      tertiary: Jetons.or,
      onTertiary: Colors.white,
      error: Jetons.danger,
      onError: Colors.white,
      surface: Jetons.surface,
      onSurface: Jetons.texte,
    );

    final texteBase = GoogleFonts.plusJakartaSansTextTheme();

    return ThemeData(
      useMaterial3: true,
      colorScheme: schema,
      scaffoldBackgroundColor: Jetons.fond,
      textTheme: texteBase.apply(
        bodyColor: Jetons.texte,
        displayColor: Jetons.texte,
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: Jetons.marine,
        foregroundColor: Colors.white,
        centerTitle: false,
        elevation: 0,
      ),
      cardTheme: CardThemeData(
        color: Jetons.surface,
        elevation: 1,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(Jetons.rayonCarte),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Jetons.surface,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(Jetons.rayonChamp),
          borderSide: const BorderSide(color: Jetons.bordure),
        ),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          minimumSize: const Size.fromHeight(Jetons.cibleTactile),
          backgroundColor: Jetons.marine,
          foregroundColor: Colors.white,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(Jetons.rayonChamp),
          ),
        ),
      ),
      navigationBarTheme: const NavigationBarThemeData(
        backgroundColor: Jetons.surface,
        indicatorColor: Jetons.orClair,
      ),
    );
  }
}
