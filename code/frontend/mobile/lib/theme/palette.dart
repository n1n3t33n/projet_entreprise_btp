import 'package:flutter/material.dart';

import '../l10n/traductions.dart';
import 'jetons.dart';

/// Rôles de couleur de l'interface, déclinés en thème clair et sombre.
///
/// Les écrans ne nomment jamais une couleur brute : ils demandent un rôle
/// (« fond », « texte secondaire », « danger »…). Changer de thème revient à
/// changer de palette, sans toucher aux écrans.
@immutable
class Palette extends ThemeExtension<Palette> {
  const Palette({
    required this.sombre,
    required this.fond,
    required this.fondAlt,
    required this.surface,
    required this.surfaceHaute,
    required this.bordure,
    required this.texte,
    required this.texteSecondaire,
    required this.texteAttenue,
    required this.primaire,
    required this.surPrimaire,
    required this.accent,
    required this.accentFond,
    required this.or,
    required this.orFond,
    required this.orBordure,
    required this.succes,
    required this.succesFond,
    required this.danger,
    required this.dangerFond,
    required this.enteteDebut,
    required this.enteteFin,
    required this.ombre,
  });

  final bool sombre;

  /// Arrière-plan de page, puis variante pour les blocs enfoncés.
  final Color fond;
  final Color fondAlt;

  /// Cartes, puis surface surélevée (feuilles, barres flottantes).
  final Color surface;
  final Color surfaceHaute;
  final Color bordure;

  final Color texte;
  final Color texteSecondaire;
  final Color texteAttenue;

  /// Action principale et son texte.
  final Color primaire;
  final Color surPrimaire;

  /// Liens et accents interactifs, avec leur fond doux.
  final Color accent;
  final Color accentFond;

  /// Alertes de seuil et éléments à surveiller.
  final Color or;
  final Color orFond;
  final Color orBordure;

  final Color succes;
  final Color succesFond;
  final Color danger;
  final Color dangerFond;

  /// Dégradé des en-têtes marine (reste marine dans les deux thèmes).
  final Color enteteDebut;
  final Color enteteFin;

  /// Teinte des ombres portées.
  final Color ombre;

  static const Palette clair = Palette(
    sombre: false,
    fond: Color(0xFFF3F8FC),
    fondAlt: Color(0xFFEAF2F9),
    surface: Color(0xFFFFFFFF),
    surfaceHaute: Color(0xFFFFFFFF),
    bordure: Color(0xFFE3EDF5),
    texte: Color(0xFF2B3A4A),
    texteSecondaire: Color(0xFF5A6572),
    texteAttenue: Color(0xFF7B8794),
    primaire: Jetons.marine,
    surPrimaire: Colors.white,
    accent: Color(0xFF1A6F94),
    accentFond: Color(0xFFE3F2FA),
    or: Jetons.or,
    orFond: Jetons.orClair,
    orBordure: Jetons.orVif,
    succes: Color(0xFF2E7D32),
    succesFond: Color(0xFFE8F5E9),
    danger: Color(0xFFC0392B),
    dangerFond: Color(0xFFFBEAE8),
    enteteDebut: Color(0xFF002E5E),
    enteteFin: Color(0xFF01407D),
    ombre: Color(0xFF002E5E),
  );

  static const Palette nuit = Palette(
    sombre: true,
    fond: Color(0xFF071A2E),
    fondAlt: Color(0xFF0B2239),
    surface: Color(0xFF0F2A47),
    surfaceHaute: Color(0xFF14355A),
    bordure: Color(0xFF214668),
    texte: Color(0xFFE9F0F7),
    texteSecondaire: Color(0xFFB1C2D3),
    texteAttenue: Color(0xFF8AA0B6),
    primaire: Color(0xFF7CCBEA),
    surPrimaire: Color(0xFF00213F),
    accent: Color(0xFF7CCBEA),
    accentFond: Color(0xFF123B5C),
    or: Jetons.sable,
    orFond: Color(0xFF3A300F),
    orBordure: Color(0xFF6B5716),
    succes: Color(0xFF86D391),
    succesFond: Color(0xFF12361B),
    danger: Color(0xFFFF9485),
    dangerFond: Color(0xFF431915),
    enteteDebut: Color(0xFF0A2644),
    enteteFin: Color(0xFF103A66),
    ombre: Color(0xFF000000),
  );

  /// Ombre douce d'une carte posée.
  List<BoxShadow> get ombreDouce => [
    BoxShadow(
      color: ombre.withValues(alpha: sombre ? 0.30 : 0.06),
      blurRadius: 16,
      offset: const Offset(0, 4),
    ),
  ];

  /// Ombre d'un élément flottant (bouton d'action, barre de navigation).
  List<BoxShadow> get ombreLevee => [
    BoxShadow(
      color: ombre.withValues(alpha: sombre ? 0.45 : 0.16),
      blurRadius: 28,
      offset: const Offset(0, 12),
    ),
  ];

  @override
  Palette copyWith() => this;

  /// Bascule franche à mi-course : un changement de thème n'a pas besoin
  /// d'interpoler vingt couleurs une à une.
  @override
  Palette lerp(ThemeExtension<Palette>? autre, double t) {
    if (autre is! Palette) return this;
    return t < 0.5 ? this : autre;
  }
}

/// Raccourcis de contexte : palette du thème courant et textes traduits.
extension ContexteChantierSync on BuildContext {
  Palette get palette => Theme.of(this).extension<Palette>() ?? Palette.clair;

  Traductions get t => Traductions.of(this);

  /// Vrai si l'utilisateur a demandé de réduire les animations.
  bool get animationsReduites =>
      MediaQuery.maybeOf(this)?.disableAnimations ?? false;
}
