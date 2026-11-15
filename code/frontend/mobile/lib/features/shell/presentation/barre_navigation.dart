import 'dart:ui';

import 'package:flutter/material.dart';

import '../../../core/navigation/onglet_role.dart';
import '../../../theme/animations.dart';
import '../../../theme/jetons.dart';
import '../../../theme/palette.dart';

/// Espace à réserver en bas des listes pour que le dernier élément ne reste
/// pas caché sous la barre de navigation flottante.
const double espaceBarreBasse = 108;

/// Barre de navigation basse, flottante et arrondie, filtrée par rôle.
///
/// Le verre dépoli a ici une fonction précise : laisser deviner le contenu
/// qui défile dessous, pour montrer que la liste continue.
class BarreNavigation extends StatelessWidget {
  const BarreNavigation({
    required this.onglets,
    required this.courant,
    required this.onSelection,
    this.pastilles = const {},
    super.key,
  });

  final List<OngletRole> onglets;
  final OngletRole courant;
  final ValueChanged<OngletRole> onSelection;

  /// Compteur affiché sur un onglet (ex. nombre d'éléments à valider).
  final Map<OngletRole, int> pastilles;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    return SafeArea(
      top: false,
      child: Padding(
        padding: const EdgeInsets.fromLTRB(12, 0, 12, 10),
        child: DecoratedBox(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(30),
            boxShadow: p.ombreLevee,
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(30),
            child: BackdropFilter(
              filter: ImageFilter.blur(sigmaX: 18, sigmaY: 18),
              child: Container(
                height: 72,
                padding: const EdgeInsets.symmetric(horizontal: 6),
                decoration: BoxDecoration(
                  color: p.surfaceHaute.withValues(
                    alpha: p.sombre ? 0.82 : 0.86,
                  ),
                  borderRadius: BorderRadius.circular(30),
                  border: Border.all(color: p.bordure),
                ),
                child: Row(
                  children: [
                    for (final onglet in onglets)
                      Expanded(
                        child: _Onglet(
                          onglet: onglet,
                          actif: onglet == courant,
                          pastille: pastilles[onglet] ?? 0,
                          onTap: () => onSelection(onglet),
                        ),
                      ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _Onglet extends StatelessWidget {
  const _Onglet({
    required this.onglet,
    required this.actif,
    required this.pastille,
    required this.onTap,
  });

  final OngletRole onglet;
  final bool actif;
  final int pastille;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final t = context.t;
    final couleur = actif
        ? (p.sombre ? p.accent : Jetons.marine)
        : p.texteSecondaire;
    final libelle = onglet.libelle(t);

    return Semantics(
      button: true,
      selected: actif,
      label: pastille > 0 ? '$libelle, $pastille' : libelle,
      child: Appui(
        onTap: onTap,
        echelle: 0.94,
        child: ExcludeSemantics(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Stack(
                clipBehavior: Clip.none,
                children: [
                  AnimatedContainer(
                    duration: Jetons.dureeNormale,
                    curve: Jetons.courbe,
                    padding: const EdgeInsets.symmetric(
                      horizontal: 18,
                      vertical: 5,
                    ),
                    decoration: BoxDecoration(
                      color: actif ? p.accentFond : Colors.transparent,
                      borderRadius: BorderRadius.circular(Jetons.rayonPilule),
                    ),
                    child: Icon(
                      actif ? onglet.iconeActive : onglet.icone,
                      color: couleur,
                      size: 24,
                    ),
                  ),
                  if (pastille > 0)
                    Positioned(
                      right: 6,
                      top: -4,
                      child: Container(
                        constraints: const BoxConstraints(minWidth: 18),
                        padding: const EdgeInsets.symmetric(
                          horizontal: 5,
                          vertical: 1,
                        ),
                        decoration: BoxDecoration(
                          color: p.or,
                          borderRadius: BorderRadius.circular(
                            Jetons.rayonPilule,
                          ),
                          border: Border.all(color: p.surfaceHaute, width: 1.5),
                        ),
                        child: Text(
                          '$pastille',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            color: p.sombre
                                ? Jetons.marineProfond
                                : Colors.white,
                            fontSize: 11,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                      ),
                    ),
                ],
              ),
              const SizedBox(height: 3),
              Text(
                libelle,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                  fontSize: 12,
                  color: couleur,
                  fontWeight: actif ? FontWeight.w700 : FontWeight.w500,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
