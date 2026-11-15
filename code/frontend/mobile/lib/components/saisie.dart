import 'package:flutter/material.dart';
import 'package:phosphor_flutter/phosphor_flutter.dart';

import '../theme/animations.dart';
import '../theme/jetons.dart';
import '../theme/palette.dart';
import 'surfaces.dart';

/// Étape numérotée d'un formulaire de terrain (1 Article, 2 Quantité…).
/// Le numéro porte une information réelle : l'ordre de saisie.
class SectionEtape extends StatelessWidget {
  const SectionEtape({
    required this.numero,
    required this.titre,
    required this.child,
    this.complement,
    super.key,
  });

  final int numero;
  final String titre;
  final Widget child;
  final Widget? complement;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    return Carte(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Container(
                width: 28,
                height: 28,
                alignment: Alignment.center,
                decoration: BoxDecoration(
                  color: p.sombre ? p.accentFond : Jetons.marine,
                  shape: BoxShape.circle,
                ),
                child: Text(
                  '$numero',
                  style: TextStyle(
                    color: p.sombre ? p.accent : Colors.white,
                    fontWeight: FontWeight.w800,
                    fontSize: 13,
                  ),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  titre,
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w700,
                    color: p.texte,
                  ),
                ),
              ),
              if (complement != null) complement!,
            ],
          ),
          const SizedBox(height: Jetons.espace3),
          child,
        ],
      ),
    );
  }
}

/// Saisie d'une quantité au doigt : gros boutons − / + et raccourcis d'ajout.
/// Pensée pour des gants de chantier : cibles de 56 px.
class SelecteurQuantite extends StatelessWidget {
  const SelecteurQuantite({
    required this.valeur,
    required this.onChange,
    required this.unite,
    this.min = 0,
    this.max,
    this.raccourcis = const [1, 5, 10],
    this.libelleMax,
    this.mention,
    super.key,
  });

  final num valeur;
  final ValueChanged<num> onChange;
  final String unite;
  final num min;
  final num? max;
  final List<num> raccourcis;

  /// Libellé du raccourci « tout » (ex. « Max (12) ») ; absent si `max` est nul.
  final String? libelleMax;

  /// Mention sous la valeur (ex. « sur 12 »).
  final String? mention;

  num _borner(num v) {
    final bas = v < min ? min : v;
    final plafond = max;
    return plafond != null && bas > plafond ? plafond : bas;
  }

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final t = context.t;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Bloc(
          padding: const EdgeInsets.all(10),
          child: Row(
            children: [
              _BoutonPas(
                icone: PhosphorIconsBold.minus,
                libelle: t.diminuer,
                plein: false,
                onTap: valeur > min
                    ? () => onChange(_borner(valeur - 1))
                    : null,
              ),
              Expanded(
                child: Column(
                  children: [
                    NombreAnime(
                      valeur: valeur,
                      style: TextStyle(
                        fontSize: 40,
                        fontWeight: FontWeight.w800,
                        height: 1.05,
                        color: p.sombre ? p.texte : Jetons.marine,
                        fontFeatures: const [FontFeature.tabularFigures()],
                      ),
                    ),
                    Text(
                      mention == null ? unite : '$unite · $mention',
                      style: TextStyle(
                        color: p.accent,
                        fontWeight: FontWeight.w700,
                        fontSize: 12.5,
                      ),
                    ),
                  ],
                ),
              ),
              _BoutonPas(
                icone: PhosphorIconsBold.plus,
                libelle: t.augmenter,
                plein: true,
                onTap: max == null || valeur < max!
                    ? () => onChange(_borner(valeur + 1))
                    : null,
              ),
            ],
          ),
        ),
        const SizedBox(height: 10),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            for (final pas in raccourcis)
              PuceChoix(
                libelle: '+$pas',
                selectionnee: false,
                onTap: () => onChange(_borner(valeur + pas)),
              ),
            if (max != null && libelleMax != null)
              PuceChoix(
                libelle: libelleMax!,
                selectionnee: valeur == max,
                onTap: () => onChange(max!),
              ),
          ],
        ),
      ],
    );
  }
}

class _BoutonPas extends StatelessWidget {
  const _BoutonPas({
    required this.icone,
    required this.libelle,
    required this.plein,
    required this.onTap,
  });

  final IconData icone;
  final String libelle;
  final bool plein;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    return Semantics(
      button: true,
      enabled: onTap != null,
      label: libelle,
      child: Appui(
        onTap: onTap,
        echelle: 0.93,
        child: Opacity(
          opacity: onTap == null ? 0.4 : 1,
          child: Container(
            width: 60,
            height: 60,
            alignment: Alignment.center,
            decoration: BoxDecoration(
              color: plein ? p.primaire : p.surface,
              borderRadius: BorderRadius.circular(Jetons.rayonChamp),
              border: plein ? null : Border.all(color: p.bordure, width: 1.5),
            ),
            child: Icon(
              icone,
              color: plein ? p.surPrimaire : p.texte,
              size: 24,
            ),
          ),
        ),
      ),
    );
  }
}

/// Puce de choix en pilule (filtre, motif, corps d'état).
class PuceChoix extends StatelessWidget {
  const PuceChoix({
    required this.libelle,
    required this.selectionnee,
    required this.onTap,
    this.icone,
    this.compteur,
    this.ton = Ton.info,
    super.key,
  });

  final String libelle;
  final bool selectionnee;
  final VoidCallback? onTap;
  final IconData? icone;
  final int? compteur;
  final Ton ton;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final couleur = selectionnee ? ton.texte(p) : p.texteSecondaire;
    return Semantics(
      button: true,
      selected: selectionnee,
      label: compteur == null ? libelle : '$libelle, $compteur',
      child: Appui(
        onTap: onTap,
        child: AnimatedContainer(
          duration: Jetons.dureeMicro,
          curve: Jetons.courbe,
          constraints: const BoxConstraints(minHeight: 44),
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 9),
          decoration: BoxDecoration(
            color: selectionnee ? ton.fond(p) : p.surface,
            borderRadius: BorderRadius.circular(Jetons.rayonPilule),
            border: Border.all(
              color: selectionnee ? couleur : p.bordure,
              width: 1.5,
            ),
          ),
          child: ExcludeSemantics(
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                if (selectionnee && icone == null) ...[
                  Icon(PhosphorIconsBold.check, size: 14, color: couleur),
                  const SizedBox(width: 6),
                ],
                if (icone != null) ...[
                  Icon(icone, size: 16, color: couleur),
                  const SizedBox(width: 6),
                ],
                Flexible(
                  child: Text(
                    libelle,
                    style: TextStyle(
                      color: selectionnee ? couleur : p.texte,
                      fontWeight: FontWeight.w600,
                      fontSize: 14,
                    ),
                  ),
                ),
                if (compteur != null) ...[
                  const SizedBox(width: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 7,
                      vertical: 1,
                    ),
                    decoration: BoxDecoration(
                      color: selectionnee
                          ? couleur.withValues(alpha: 0.16)
                          : p.fondAlt,
                      borderRadius: BorderRadius.circular(Jetons.rayonPilule),
                    ),
                    child: Text(
                      '$compteur',
                      style: TextStyle(
                        color: couleur,
                        fontWeight: FontWeight.w700,
                        fontSize: 12,
                      ),
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// Carte d'option exclusive (bouton radio étendu) : icône, titre, précision.
class CarteOption extends StatelessWidget {
  const CarteOption({
    required this.titre,
    required this.selectionnee,
    required this.onTap,
    this.detail,
    this.icone,
    this.ton = Ton.info,
    super.key,
  });

  final String titre;
  final String? detail;
  final IconData? icone;
  final bool selectionnee;
  final VoidCallback? onTap;
  final Ton ton;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final couleur = ton.texte(p);
    return Semantics(
      inMutuallyExclusiveGroup: true,
      checked: selectionnee,
      button: true,
      child: Appui(
        onTap: onTap,
        echelle: 0.985,
        child: AnimatedContainer(
          duration: Jetons.dureeMicro,
          curve: Jetons.courbe,
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: selectionnee ? ton.fond(p) : p.surface,
            borderRadius: BorderRadius.circular(Jetons.rayonBloc),
            border: Border.all(
              color: selectionnee ? couleur : p.bordure,
              width: selectionnee ? 2 : 1.5,
            ),
          ),
          child: Row(
            children: [
              if (icone != null) ...[
                TuileIcone(
                  icone: icone!,
                  ton: selectionnee ? ton : Ton.neutre,
                  taille: 40,
                ),
                const SizedBox(width: 12),
              ],
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      titre,
                      style: TextStyle(
                        fontWeight: FontWeight.w700,
                        fontSize: 15,
                        color: p.texte,
                      ),
                    ),
                    if (detail != null)
                      Text(
                        detail!,
                        style: TextStyle(
                          color: p.texteSecondaire,
                          fontSize: 13,
                          height: 1.3,
                        ),
                      ),
                  ],
                ),
              ),
              const SizedBox(width: 8),
              Icon(
                selectionnee
                    ? PhosphorIconsFill.checkCircle
                    : PhosphorIconsRegular.circle,
                color: selectionnee ? couleur : p.texteAttenue,
                size: 24,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Libellé d'un champ, en petites capitales discrètes au-dessus de la saisie.
class LibelleChamp extends StatelessWidget {
  const LibelleChamp(this.texte, {this.requis = false, super.key});

  final String texte;
  final bool requis;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Text.rich(
        TextSpan(
          text: texte,
          children: [
            if (requis)
              TextSpan(
                text: ' *',
                style: TextStyle(color: p.danger),
              ),
          ],
        ),
        style: TextStyle(
          color: p.texteSecondaire,
          fontWeight: FontWeight.w600,
          fontSize: 13,
        ),
      ),
    );
  }
}
