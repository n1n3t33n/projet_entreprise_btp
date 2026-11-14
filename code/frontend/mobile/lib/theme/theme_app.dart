import 'package:flutter/material.dart';

import 'jetons.dart';
import 'palette.dart';

/// Construit les thèmes Material 3 de ChantierSync (clair et sombre) à partir
/// des [Jetons] et d'une [Palette]. La police Plus Jakarta Sans est embarquée :
/// l'application n'a besoin d'aucun réseau pour s'afficher correctement.
abstract final class ThemeApp {
  static ThemeData clair() => _construire(Palette.clair);

  static ThemeData sombre() => _construire(Palette.nuit);

  static ThemeData _construire(Palette p) {
    final schema = ColorScheme(
      brightness: p.sombre ? Brightness.dark : Brightness.light,
      primary: p.primaire,
      onPrimary: p.surPrimaire,
      secondary: p.accent,
      onSecondary: p.surPrimaire,
      tertiary: p.or,
      onTertiary: p.surPrimaire,
      error: p.danger,
      onError: p.sombre ? const Color(0xFF3B0D08) : Colors.white,
      surface: p.surface,
      onSurface: p.texte,
    );

    final base = ThemeData(
      useMaterial3: true,
      brightness: schema.brightness,
      colorScheme: schema,
      fontFamily: Jetons.police,
    );

    final forme = RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(Jetons.rayonChamp),
    );
    OutlineInputBorder contour(Color couleur, [double largeur = 1]) {
      return OutlineInputBorder(
        borderRadius: BorderRadius.circular(Jetons.rayonChamp),
        borderSide: BorderSide(color: couleur, width: largeur),
      );
    }

    return base.copyWith(
      scaffoldBackgroundColor: p.fond,
      extensions: [p],
      textTheme: base.textTheme.apply(
        bodyColor: p.texte,
        displayColor: p.texte,
      ),
      dividerTheme: DividerThemeData(color: p.bordure, thickness: 1, space: 1),
      textSelectionTheme: TextSelectionThemeData(
        cursorColor: p.accent,
        selectionColor: p.accent.withValues(alpha: 0.25),
        selectionHandleColor: p.accent,
      ),
      appBarTheme: AppBarTheme(
        backgroundColor: p.surface,
        foregroundColor: p.texte,
        surfaceTintColor: Colors.transparent,
        centerTitle: false,
        elevation: 0,
        scrolledUnderElevation: 0,
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: p.surface,
        hintStyle: TextStyle(color: p.texteAttenue),
        labelStyle: TextStyle(color: p.texteSecondaire),
        contentPadding: const EdgeInsets.symmetric(
          horizontal: Jetons.espace3,
          vertical: 18,
        ),
        border: contour(p.bordure),
        enabledBorder: contour(p.bordure),
        focusedBorder: contour(p.accent, 2),
        errorBorder: contour(p.danger),
        focusedErrorBorder: contour(p.danger, 2),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          minimumSize: const Size.fromHeight(Jetons.cibleTactile),
          backgroundColor: p.primaire,
          foregroundColor: p.surPrimaire,
          textStyle: const TextStyle(
            fontFamily: Jetons.police,
            fontWeight: FontWeight.w700,
            fontSize: 16,
          ),
          shape: const StadiumBorder(),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          minimumSize: const Size.fromHeight(Jetons.cibleTactile),
          foregroundColor: p.primaire,
          side: BorderSide(color: p.bordure, width: 1.5),
          textStyle: const TextStyle(
            fontFamily: Jetons.police,
            fontWeight: FontWeight.w700,
            fontSize: 16,
          ),
          shape: const StadiumBorder(),
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: p.accent,
          textStyle: const TextStyle(
            fontFamily: Jetons.police,
            fontWeight: FontWeight.w700,
          ),
          shape: const StadiumBorder(),
        ),
      ),
      bottomSheetTheme: BottomSheetThemeData(
        backgroundColor: p.surfaceHaute,
        surfaceTintColor: Colors.transparent,
        showDragHandle: true,
        dragHandleColor: p.bordure,
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(
            top: Radius.circular(Jetons.rayonCarte + 4),
          ),
        ),
      ),
      dialogTheme: DialogThemeData(
        backgroundColor: p.surfaceHaute,
        surfaceTintColor: Colors.transparent,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(Jetons.rayonCarte),
        ),
      ),
      snackBarTheme: SnackBarThemeData(
        behavior: SnackBarBehavior.floating,
        backgroundColor: p.sombre ? p.surfaceHaute : Jetons.marine,
        contentTextStyle: const TextStyle(
          fontFamily: Jetons.police,
          color: Colors.white,
          fontWeight: FontWeight.w600,
        ),
        shape: forme,
      ),
      progressIndicatorTheme: ProgressIndicatorThemeData(
        color: p.accent,
        linearTrackColor: p.fondAlt,
      ),
    );
  }
}
