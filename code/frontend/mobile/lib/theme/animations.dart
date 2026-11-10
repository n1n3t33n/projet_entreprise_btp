import 'package:flutter/material.dart';

import 'jetons.dart';

/// Animations de la charte (§ 7), discrètes et porteuses de sens.
///
/// On n'anime que la transformation et l'opacité (jamais les dimensions), et on
/// respecte la préférence « réduire les animations » : rendu final immédiat si
/// l'utilisateur la demande.

bool _animationsReduites(BuildContext context) =>
    MediaQuery.maybeOf(context)?.disableAnimations ?? false;

/// Apparition par fondu + légère montée. Un [delai] croissant d'un élément à
/// l'autre produit la révélation « en cascade ».
class Apparition extends StatefulWidget {
  const Apparition({
    required this.child,
    this.delai = Duration.zero,
    this.duree = Jetons.dureeNormale,
    super.key,
  });

  final Widget child;
  final Duration delai;
  final Duration duree;

  @override
  State<Apparition> createState() => _ApparitionState();
}

class _ApparitionState extends State<Apparition>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controleur = AnimationController(
    vsync: this,
    duration: widget.duree,
  );

  @override
  void initState() {
    super.initState();
    final reduit = WidgetsBinding
        .instance
        .platformDispatcher
        .accessibilityFeatures
        .disableAnimations;
    if (reduit) {
      _controleur.value = 1;
    } else if (widget.delai == Duration.zero) {
      _controleur.forward();
    } else {
      Future<void>.delayed(widget.delai, () {
        if (mounted) _controleur.forward();
      });
    }
  }

  @override
  void dispose() {
    _controleur.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_animationsReduites(context)) return widget.child;
    final courbe = CurvedAnimation(parent: _controleur, curve: Curves.easeOut);
    return FadeTransition(
      opacity: courbe,
      child: SlideTransition(
        position: Tween<Offset>(
          begin: const Offset(0, 0.06),
          end: Offset.zero,
        ).animate(courbe),
        child: widget.child,
      ),
    );
  }
}

/// Carte/tuile avec micro-retour tactile : légère lévitation (échelle) à
/// l'appui, ~160 ms. Respecte « réduire les animations ».
class CarteLevitation extends StatefulWidget {
  const CarteLevitation({required this.child, this.onTap, super.key});

  final Widget child;
  final VoidCallback? onTap;

  @override
  State<CarteLevitation> createState() => _CarteLevitationState();
}

class _CarteLevitationState extends State<CarteLevitation> {
  bool _appuye = false;

  void _definir(bool valeur) {
    if (mounted) setState(() => _appuye = valeur);
  }

  @override
  Widget build(BuildContext context) {
    final reduit = _animationsReduites(context);
    final echelle = (_appuye && !reduit) ? 0.98 : 1.0;
    return GestureDetector(
      onTap: widget.onTap,
      onTapDown: (_) => _definir(true),
      onTapUp: (_) => _definir(false),
      onTapCancel: () => _definir(false),
      child: AnimatedScale(
        scale: echelle,
        duration: Jetons.dureeMicro,
        curve: Curves.easeOut,
        child: widget.child,
      ),
    );
  }
}
