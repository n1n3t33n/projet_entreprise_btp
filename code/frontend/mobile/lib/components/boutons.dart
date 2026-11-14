import 'package:flutter/material.dart';

import '../theme/animations.dart';
import '../theme/jetons.dart';
import '../theme/palette.dart';
import 'surfaces.dart';

/// Bouton principal : pilule pleine de 56 px (cible tactile de chantier), avec
/// retour tactile et état de chargement.
class BoutonPrincipal extends StatelessWidget {
  const BoutonPrincipal({
    required this.libelle,
    required this.onPressed,
    this.icone,
    this.iconeFin,
    this.ton = Ton.marine,
    this.enChargement = false,
    super.key,
  });

  final String libelle;
  final VoidCallback? onPressed;
  final IconData? icone;

  /// Icône placée après le libellé (flèche « continuer »).
  final IconData? iconeFin;
  final Ton ton;
  final bool enChargement;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final actif = onPressed != null && !enChargement;
    final fond = switch (ton) {
      Ton.danger => p.danger,
      Ton.info => p.sombre ? p.accent : Jetons.sarcelle,
      Ton.succes => p.succes,
      _ => p.primaire,
    };
    final texte = ton == Ton.marine || p.sombre ? p.surPrimaire : Colors.white;

    return Semantics(
      button: true,
      enabled: actif,
      label: libelle,
      child: Appui(
        onTap: actif ? onPressed : null,
        child: AnimatedOpacity(
          opacity: actif || enChargement ? 1 : 0.45,
          duration: Jetons.dureeMicro,
          child: Container(
            constraints: const BoxConstraints(minHeight: Jetons.cibleTactile),
            padding: const EdgeInsets.symmetric(
              horizontal: Jetons.espace4,
              vertical: 14,
            ),
            decoration: BoxDecoration(
              color: fond,
              borderRadius: BorderRadius.circular(Jetons.rayonPilule),
              boxShadow: actif ? p.ombreLevee : null,
            ),
            child: enChargement
                ? Center(
                    child: SizedBox(
                      width: 22,
                      height: 22,
                      child: CircularProgressIndicator(
                        strokeWidth: 2.5,
                        color: texte,
                      ),
                    ),
                  )
                : Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      if (icone != null) ...[
                        Icon(icone, size: 20, color: texte),
                        const SizedBox(width: 10),
                      ],
                      Flexible(
                        child: ExcludeSemantics(
                          child: Text(
                            libelle,
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              color: texte,
                              fontWeight: FontWeight.w700,
                              fontSize: 16,
                              height: 1.25,
                            ),
                          ),
                        ),
                      ),
                      if (iconeFin != null) ...[
                        const SizedBox(width: 10),
                        Icon(iconeFin, size: 20, color: texte),
                      ],
                    ],
                  ),
          ),
        ),
      ),
    );
  }
}

/// Bouton secondaire : pilule douce ou à contour, pour les actions d'appoint.
class BoutonSecondaire extends StatelessWidget {
  const BoutonSecondaire({
    required this.libelle,
    required this.onPressed,
    this.icone,
    this.ton = Ton.info,
    this.compact = false,
    this.contour = false,
    super.key,
  });

  final String libelle;
  final VoidCallback? onPressed;
  final IconData? icone;
  final Ton ton;

  /// Vrai pour une hauteur réduite (48 px), dans une carte.
  final bool compact;

  /// Vrai pour un fond transparent avec contour.
  final bool contour;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final couleur = ton.texte(p);
    return Semantics(
      button: true,
      enabled: onPressed != null,
      label: libelle,
      child: Appui(
        onTap: onPressed,
        child: Opacity(
          opacity: onPressed == null ? 0.45 : 1,
          child: Container(
            constraints: BoxConstraints(
              minHeight: compact ? 48 : Jetons.cibleTactile,
            ),
            padding: const EdgeInsets.symmetric(
              horizontal: Jetons.espace3,
              vertical: 10,
            ),
            decoration: BoxDecoration(
              color: contour ? Colors.transparent : ton.fond(p),
              borderRadius: BorderRadius.circular(Jetons.rayonPilule),
              border: contour
                  ? Border.all(
                      color: couleur.withValues(alpha: 0.5),
                      width: 1.5,
                    )
                  : null,
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              mainAxisSize: MainAxisSize.min,
              children: [
                if (icone != null) ...[
                  Icon(icone, size: 18, color: couleur),
                  const SizedBox(width: 8),
                ],
                Flexible(
                  child: ExcludeSemantics(
                    child: Text(
                      libelle,
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        color: couleur,
                        fontWeight: FontWeight.w700,
                        fontSize: compact ? 14 : 15,
                        height: 1.25,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// Bouton rond à icône seule, toujours accompagné d'un libellé accessible.
class BoutonIcone extends StatelessWidget {
  const BoutonIcone({
    required this.icone,
    required this.libelle,
    required this.onPressed,
    this.surMarine = false,
    this.taille = 44,
    super.key,
  });

  final IconData icone;
  final String libelle;
  final VoidCallback? onPressed;
  final bool surMarine;
  final double taille;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    return Tooltip(
      message: libelle,
      child: Semantics(
        button: true,
        label: libelle,
        child: Appui(
          onTap: onPressed,
          echelle: 0.92,
          child: Container(
            width: taille,
            height: taille,
            alignment: Alignment.center,
            decoration: BoxDecoration(
              color: surMarine
                  ? Colors.white.withValues(alpha: 0.12)
                  : p.fondAlt,
              shape: BoxShape.circle,
            ),
            child: Icon(
              icone,
              size: taille * 0.48,
              color: surMarine ? Colors.white : p.texte,
            ),
          ),
        ),
      ),
    );
  }
}

/// Tuile de raccourci : une action métier en un geste (icône + libellé).
class TuileAction extends StatelessWidget {
  const TuileAction({
    required this.icone,
    required this.libelle,
    required this.onTap,
    this.ton = Ton.info,
    super.key,
  });

  final IconData icone;
  final String libelle;
  final VoidCallback? onTap;
  final Ton ton;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    return Carte(
      onTap: onTap,
      padding: const EdgeInsets.symmetric(
        horizontal: 10,
        vertical: Jetons.espace3,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          TuileIcone(icone: icone, ton: ton),
          const SizedBox(height: 10),
          Text(
            libelle,
            textAlign: TextAlign.center,
            style: TextStyle(
              fontWeight: FontWeight.w700,
              fontSize: 13,
              height: 1.25,
              color: p.texte,
            ),
          ),
        ],
      ),
    );
  }
}
