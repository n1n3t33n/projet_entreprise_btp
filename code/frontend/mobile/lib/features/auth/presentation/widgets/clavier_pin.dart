import 'package:flutter/material.dart';
import 'package:phosphor_flutter/phosphor_flutter.dart';

import '../../../../theme/animations.dart';
import '../../../../theme/jetons.dart';

/// Points indiquant les chiffres déjà saisis du PIN (charte : marine plein /
/// contour atténué).
class PointsPin extends StatelessWidget {
  const PointsPin({required this.remplis, this.total = 6, super.key});

  final int remplis;
  final int total;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        for (var i = 0; i < total; i++)
          AnimatedContainer(
            duration: Jetons.dureeMicro,
            curve: Curves.easeOut,
            margin: const EdgeInsets.symmetric(horizontal: 6),
            width: 18,
            height: 18,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: i < remplis ? Jetons.marine : Colors.transparent,
              border: Border.all(
                color: i < remplis ? Jetons.marine : Jetons.texteAttenue,
                width: 2,
              ),
            ),
          ),
      ],
    );
  }
}

/// Clavier numérique du PIN (3×4), cibles tactiles généreuses. Dernière ligne :
/// RAZ, 0, effacement.
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
    return Column(
      children: [
        _ligne(['1', '2', '3']),
        _ligne(['4', '5', '6']),
        _ligne(['7', '8', '9']),
        Row(
          children: [
            Expanded(
              child: _ToucheAction(
                icone: PhosphorIconsRegular.arrowCounterClockwise,
                libelle: 'RAZ',
                onTap: onRaz,
              ),
            ),
            Expanded(
              child: _ToucheChiffre(chiffre: '0', onTap: onChiffre),
            ),
            Expanded(
              child: _ToucheAction(
                icone: PhosphorIconsRegular.backspace,
                onTap: onEffacer,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _ligne(List<String> chiffres) {
    return Row(
      children: [
        for (final chiffre in chiffres)
          Expanded(
            child: _ToucheChiffre(chiffre: chiffre, onTap: onChiffre),
          ),
      ],
    );
  }
}

class _ToucheChiffre extends StatelessWidget {
  const _ToucheChiffre({required this.chiffre, required this.onTap});

  final String chiffre;
  final void Function(String) onTap;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(Jetons.espace2 / 2),
      child: CarteLevitation(
        onTap: () => onTap(chiffre),
        child: Container(
          height: 64,
          alignment: Alignment.center,
          decoration: BoxDecoration(
            color: Jetons.surface,
            borderRadius: BorderRadius.circular(Jetons.rayonChamp),
            border: Border.all(color: Jetons.bordure),
          ),
          child: Text(
            chiffre,
            style: const TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.w600,
              color: Jetons.marine,
            ),
          ),
        ),
      ),
    );
  }
}

class _ToucheAction extends StatelessWidget {
  const _ToucheAction({required this.icone, required this.onTap, this.libelle});

  final IconData icone;
  final String? libelle;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(Jetons.espace2 / 2),
      child: CarteLevitation(
        onTap: onTap,
        child: Container(
          height: 64,
          alignment: Alignment.center,
          decoration: BoxDecoration(
            color: Jetons.fondSection,
            borderRadius: BorderRadius.circular(Jetons.rayonChamp),
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icone, color: Jetons.texteSecondaire),
              if (libelle != null)
                Text(
                  libelle!,
                  style: const TextStyle(
                    fontSize: 11,
                    color: Jetons.texteSecondaire,
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}
