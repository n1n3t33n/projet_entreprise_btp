import 'package:flutter/material.dart';

import 'jetons.dart';
import 'palette.dart';

/// Animations de la charte (§ 7), discrètes et porteuses de sens.
///
/// On n'anime que la transformation et l'opacité (jamais les dimensions), et
/// l'on respecte la préférence « réduire les animations » : le rendu final est
/// alors immédiat.

/// Apparition par fondu + légère montée. Un [rang] croissant d'un élément à
/// l'autre produit la révélation « en cascade » d'une liste.
class Apparition extends StatefulWidget {
  const Apparition({required this.child, this.rang = 0, super.key});

  final Widget child;

  /// Position dans la cascade : chaque rang retarde l'entrée d'un pas.
  final int rang;

  @override
  State<Apparition> createState() => _ApparitionState();
}

class _ApparitionState extends State<Apparition>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controleur;
  late final Animation<double> _progression;

  @override
  void initState() {
    super.initState();
    // Le délai fait partie de l'animation elle-même (intervalle) : aucun
    // minuteur à annuler si l'écran se ferme avant la fin.
    final rang = widget.rang.clamp(0, 8);
    final delai = Jetons.pasCascade * rang;
    final total = delai + Jetons.dureeNormale;
    _controleur = AnimationController(vsync: this, duration: total);
    _progression = CurvedAnimation(
      parent: _controleur,
      curve: Interval(
        delai.inMilliseconds / total.inMilliseconds,
        1,
        curve: Jetons.courbe,
      ),
    );
    final reduit = WidgetsBinding
        .instance
        .platformDispatcher
        .accessibilityFeatures
        .disableAnimations;
    if (reduit) {
      _controleur.value = 1;
    } else {
      _controleur.forward();
    }
  }

  @override
  void dispose() {
    _controleur.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (context.animationsReduites) return widget.child;
    return FadeTransition(
      opacity: _progression,
      child: SlideTransition(
        position: Tween<Offset>(
          begin: const Offset(0, 0.05),
          end: Offset.zero,
        ).animate(_progression),
        child: widget.child,
      ),
    );
  }
}

/// Retour tactile : l'élément s'enfonce très légèrement sous le doigt
/// (≈ 160 ms), pour confirmer que l'appui est pris en compte.
class Appui extends StatefulWidget {
  const Appui({
    required this.child,
    this.onTap,
    this.echelle = 0.97,
    super.key,
  });

  final Widget child;
  final VoidCallback? onTap;
  final double echelle;

  @override
  State<Appui> createState() => _AppuiState();
}

class _AppuiState extends State<Appui> {
  bool _appuye = false;

  void _definir(bool valeur) {
    if (mounted && widget.onTap != null) setState(() => _appuye = valeur);
  }

  @override
  Widget build(BuildContext context) {
    final actif = _appuye && !context.animationsReduites;
    return GestureDetector(
      behavior: HitTestBehavior.opaque,
      onTap: widget.onTap,
      onTapDown: (_) => _definir(true),
      onTapUp: (_) => _definir(false),
      onTapCancel: () => _definir(false),
      child: AnimatedScale(
        scale: actif ? widget.echelle : 1,
        duration: Jetons.dureeMicro,
        curve: Jetons.courbe,
        child: widget.child,
      ),
    );
  }
}

/// Nombre qui glisse vers sa nouvelle valeur quand elle change (compteur de
/// quantité, indicateur). Sans mouvement si les animations sont réduites.
class NombreAnime extends StatelessWidget {
  const NombreAnime({
    required this.valeur,
    required this.style,
    this.suffixe = '',
    super.key,
  });

  final num valeur;
  final TextStyle style;
  final String suffixe;

  @override
  Widget build(BuildContext context) {
    String formater(double v) {
      final entier = valeur is int || valeur == valeur.roundToDouble();
      return '${entier ? v.round() : v.toStringAsFixed(1)}$suffixe';
    }

    if (context.animationsReduites) {
      return Text(formater(valeur.toDouble()), style: style);
    }
    return TweenAnimationBuilder<double>(
      tween: Tween<double>(end: valeur.toDouble()),
      duration: Jetons.dureeNormale,
      curve: Jetons.courbe,
      builder: (_, v, _) => Text(formater(v), style: style),
    );
  }
}
