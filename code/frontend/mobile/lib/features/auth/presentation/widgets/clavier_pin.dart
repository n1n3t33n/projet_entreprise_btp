import 'package:flutter/material.dart';
import 'package:phosphor_flutter/phosphor_flutter.dart';

import '../../../../theme/animations.dart';
import '../../../../theme/jetons.dart';
import '../../../../theme/palette.dart';

/// Nombre de chiffres du code PIN de chantier.
const int longueurPin = 6;

/// Points indiquant les chiffres déjà saisis du PIN. En cas d'erreur, la
/// rangée se teinte en rouge le temps que l'opérateur ressaisisse.
class PointsPin extends StatelessWidget {
  const PointsPin({required this.remplis, this.erreur = false, super.key});

  final int remplis;
  final bool erreur;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final plein = erreur ? p.danger : (p.sombre ? p.accent : Jetons.marine);
    return Semantics(
      label: context.t.pinSaisi(remplis, longueurPin),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          for (var i = 0; i < longueurPin; i++)
            AnimatedContainer(
              duration: Jetons.dureeMicro,
              curve: Jetons.courbe,
              margin: const EdgeInsets.symmetric(horizontal: 7),
              width: 18,
              height: 18,
              transform: Matrix4.diagonal3Values(
                i < remplis ? 1.0 : 0.82,
                i < remplis ? 1.0 : 0.82,
                1,
              ),
              transformAlignment: Alignment.center,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: i < remplis ? plein : Colors.transparent,
                border: Border.all(
                  color: i < remplis ? plein : p.texteAttenue,
                  width: 2,
                ),
              ),
            ),
        ],
      ),
    );
  }
}

/// Clavier numérique du PIN (3 × 4), cibles tactiles généreuses. Dernière
/// ligne : remise à zéro, 0, effacement.
class ClavierPin extends StatelessWidget {
  const ClavierPin({
    required this.onChiffre,
    required this.onEffacer,
    required this.onRaz,
    super.key,
  });

  final void Function(String chiffre) onChiffre;
  final VoidCallback onEffacer;
  final VoidCallback onRaz;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    return Column(
      children: [
        for (final ligne in const [
          ['1', '2', '3'],
          ['4', '5', '6'],
          ['7', '8', '9'],
        ])
          Row(
            children: [
              for (final chiffre in ligne)
                Expanded(
                  child: _Touche(
                    libelle: chiffre,
                    onTap: () => onChiffre(chiffre),
                    child: _Chiffre(chiffre),
                  ),
                ),
            ],
          ),
        Row(
          children: [
            Expanded(
              child: _Touche(
                libelle: t.pinRaz,
                onTap: onRaz,
                secondaire: true,
                child: _Action(
                  icone: PhosphorIconsRegular.arrowCounterClockwise,
                  texte: t.pinRaz,
                ),
              ),
            ),
            Expanded(
              child: _Touche(
                libelle: '0',
                onTap: () => onChiffre('0'),
                child: const _Chiffre('0'),
              ),
            ),
            Expanded(
              child: _Touche(
                libelle: t.pinEffacer,
                onTap: onEffacer,
                secondaire: true,
                child: const _Action(icone: PhosphorIconsRegular.backspace),
              ),
            ),
          ],
        ),
      ],
    );
  }
}

class _Touche extends StatelessWidget {
  const _Touche({
    required this.libelle,
    required this.onTap,
    required this.child,
    this.secondaire = false,
  });

  final String libelle;
  final VoidCallback onTap;
  final Widget child;
  final bool secondaire;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    return Padding(
      padding: const EdgeInsets.all(5),
      child: Semantics(
        button: true,
        label: libelle,
        child: Appui(
          onTap: onTap,
          echelle: 0.94,
          child: Container(
            height: 62,
            alignment: Alignment.center,
            decoration: BoxDecoration(
              color: secondaire ? p.fondAlt : p.surface,
              borderRadius: BorderRadius.circular(Jetons.rayonBloc),
              border: secondaire ? null : Border.all(color: p.bordure),
              boxShadow: secondaire ? null : p.ombreDouce,
            ),
            child: ExcludeSemantics(child: child),
          ),
        ),
      ),
    );
  }
}

class _Chiffre extends StatelessWidget {
  const _Chiffre(this.chiffre);

  final String chiffre;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    return Text(
      chiffre,
      style: TextStyle(
        fontSize: 24,
        fontWeight: FontWeight.w700,
        color: p.sombre ? p.texte : Jetons.marine,
      ),
    );
  }
}

class _Action extends StatelessWidget {
  const _Action({required this.icone, this.texte});

  final IconData icone;
  final String? texte;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(icone, color: p.texteSecondaire, size: 22),
        if (texte != null)
          Text(
            texte!,
            style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w700,
              color: p.texteSecondaire,
            ),
          ),
      ],
    );
  }
}
