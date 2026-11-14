import 'package:flutter/material.dart';

import '../core/outils/identifiants.dart';
import '../theme/animations.dart';
import '../theme/jetons.dart';
import '../theme/palette.dart';

/// Tonalité d'un élément d'état. Un statut n'est jamais porté par la couleur
/// seule : il s'accompagne toujours d'une icône et d'un libellé (charte § 2).
enum Ton { neutre, info, succes, alerte, danger, marine }

extension CouleursTon on Ton {
  Color texte(Palette p) => switch (this) {
    Ton.neutre => p.texteSecondaire,
    Ton.info => p.accent,
    Ton.succes => p.succes,
    Ton.alerte => p.or,
    Ton.danger => p.danger,
    Ton.marine => p.sombre ? p.texte : Jetons.marine,
  };

  Color fond(Palette p) => switch (this) {
    Ton.neutre => p.fondAlt,
    Ton.info => p.accentFond,
    Ton.succes => p.succesFond,
    Ton.alerte => p.orFond,
    Ton.danger => p.dangerFond,
    Ton.marine => p.accentFond,
  };
}

/// Carte : surface blanche arrondie, bordure fine et ombre douce.
class Carte extends StatelessWidget {
  const Carte({
    required this.child,
    this.padding = const EdgeInsets.all(Jetons.espace3),
    this.couleur,
    this.bordure,
    this.rayon = Jetons.rayonCarte,
    this.onTap,
    this.avecOmbre = true,
    super.key,
  });

  final Widget child;
  final EdgeInsetsGeometry padding;
  final Color? couleur;
  final Color? bordure;
  final double rayon;
  final VoidCallback? onTap;
  final bool avecOmbre;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final carte = Container(
      padding: padding,
      decoration: BoxDecoration(
        color: couleur ?? p.surface,
        borderRadius: BorderRadius.circular(rayon),
        border: Border.all(color: bordure ?? p.bordure),
        boxShadow: avecOmbre ? p.ombreDouce : null,
      ),
      child: child,
    );
    if (onTap == null) return carte;
    return Semantics(
      button: true,
      child: Appui(onTap: onTap, echelle: 0.985, child: carte),
    );
  }
}

/// Bloc enfoncé à l'intérieur d'une carte (fond alterné, sans ombre).
class Bloc extends StatelessWidget {
  const Bloc({
    required this.child,
    this.padding = const EdgeInsets.all(Jetons.espace3),
    this.couleur,
    this.bordure,
    super.key,
  });

  final Widget child;
  final EdgeInsetsGeometry padding;
  final Color? couleur;
  final Color? bordure;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    return Container(
      padding: padding,
      decoration: BoxDecoration(
        color: couleur ?? p.fondAlt,
        borderRadius: BorderRadius.circular(Jetons.rayonBloc),
        border: bordure == null ? null : Border.all(color: bordure!),
      ),
      child: child,
    );
  }
}

/// Pilule de statut : icône + libellé, dans la tonalité de l'état.
class Pastille extends StatelessWidget {
  const Pastille({
    required this.libelle,
    this.icone,
    this.ton = Ton.neutre,
    this.pleine = false,
    super.key,
  });

  final String libelle;
  final IconData? icone;
  final Ton ton;

  /// Vrai pour une pastille pleine (texte clair sur couleur forte).
  final bool pleine;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final couleurTexte = pleine ? p.surface : ton.texte(p);
    final couleurFond = pleine ? ton.texte(p) : ton.fond(p);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: couleurFond,
        borderRadius: BorderRadius.circular(Jetons.rayonPilule),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (icone != null) ...[
            Icon(icone, size: 14, color: couleurTexte),
            const SizedBox(width: 5),
          ],
          Flexible(
            child: Text(
              libelle,
              style: TextStyle(
                color: couleurTexte,
                fontSize: 12,
                fontWeight: FontWeight.w700,
                height: 1.2,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

/// Icône posée dans une tuile arrondie de la tonalité donnée.
class TuileIcone extends StatelessWidget {
  const TuileIcone({
    required this.icone,
    this.ton = Ton.info,
    this.taille = 44,
    super.key,
  });

  final IconData icone;
  final Ton ton;
  final double taille;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    return Container(
      width: taille,
      height: taille,
      alignment: Alignment.center,
      decoration: BoxDecoration(
        color: ton.fond(p),
        borderRadius: BorderRadius.circular(taille * 0.34),
      ),
      child: Icon(icone, color: ton.texte(p), size: taille * 0.5),
    );
  }
}

/// Barre d'avancement : le remplissage s'étire par transformation (jamais par
/// changement de largeur), de 0 à 1.
class BarreProgression extends StatelessWidget {
  const BarreProgression({
    required this.valeur,
    this.ton = Ton.info,
    this.hauteur = 8,
    super.key,
  });

  final double valeur;
  final Ton ton;
  final double hauteur;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final cible = valeur.clamp(0.0, 1.0);
    return Semantics(
      value: '${(cible * 100).round()} %',
      child: ClipRRect(
        borderRadius: BorderRadius.circular(hauteur),
        child: Container(
          height: hauteur,
          color: p.fondAlt,
          alignment: Alignment.centerLeft,
          child: TweenAnimationBuilder<double>(
            tween: Tween<double>(end: cible),
            duration: context.animationsReduites
                ? Duration.zero
                : const Duration(milliseconds: 420),
            curve: Jetons.courbe,
            builder: (_, v, _) => FractionallySizedBox(
              widthFactor: 1,
              child: Transform.scale(
                scaleX: v,
                alignment: Alignment.centerLeft,
                child: Container(
                  decoration: BoxDecoration(
                    color: ton.texte(p),
                    borderRadius: BorderRadius.circular(hauteur),
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

/// Titre d'une section d'écran, avec un complément facultatif à droite.
class TitreSection extends StatelessWidget {
  const TitreSection(this.titre, {this.icone, this.complement, super.key});

  final String titre;
  final IconData? icone;
  final Widget? complement;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    return Row(
      children: [
        if (icone != null) ...[
          Icon(icone, size: 20, color: p.sombre ? p.texte : Jetons.marine),
          const SizedBox(width: Jetons.espace2),
        ],
        Expanded(
          child: Text(
            titre,
            style: TextStyle(
              fontSize: 17,
              fontWeight: FontWeight.w700,
              color: p.sombre ? p.texte : Jetons.marine,
            ),
          ),
        ),
        if (complement != null) complement!,
      ],
    );
  }
}

/// Pastille ronde aux initiales d'une personne.
class AvatarInitiales extends StatelessWidget {
  const AvatarInitiales(
    this.nom, {
    this.taille = 44,
    this.surMarine = false,
    super.key,
  });

  final String nom;
  final double taille;

  /// Vrai sur un en-tête marine : fond sable, lettres marine.
  final bool surMarine;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final fond = surMarine
        ? Jetons.sable
        : (p.sombre ? p.accentFond : Jetons.marine);
    final lettres = surMarine
        ? Jetons.marine
        : (p.sombre ? p.accent : Colors.white);
    return Container(
      width: taille,
      height: taille,
      alignment: Alignment.center,
      decoration: BoxDecoration(color: fond, shape: BoxShape.circle),
      child: Text(
        initiales(nom),
        style: TextStyle(
          color: lettres,
          fontWeight: FontWeight.w800,
          fontSize: taille * 0.36,
        ),
      ),
    );
  }
}

/// État vide : explique quoi faire plutôt que d'afficher « rien ».
class EtatVide extends StatelessWidget {
  const EtatVide({
    required this.icone,
    required this.titre,
    this.texte,
    this.action,
    super.key,
  });

  final IconData icone;
  final String titre;
  final String? texte;
  final Widget? action;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    return Padding(
      padding: const EdgeInsets.all(Jetons.espace4),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          TuileIcone(icone: icone, ton: Ton.neutre, taille: 64),
          const SizedBox(height: Jetons.espace3),
          Text(
            titre,
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 17,
              fontWeight: FontWeight.w700,
              color: p.texte,
            ),
          ),
          if (texte != null) ...[
            const SizedBox(height: Jetons.espace2),
            Text(
              texte!,
              textAlign: TextAlign.center,
              style: TextStyle(color: p.texteSecondaire, height: 1.4),
            ),
          ],
          if (action != null) ...[
            const SizedBox(height: Jetons.espace3),
            action!,
          ],
        ],
      ),
    );
  }
}
