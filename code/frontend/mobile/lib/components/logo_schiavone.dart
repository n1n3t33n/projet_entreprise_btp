import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

import '../theme/jetons.dart';

/// Logo officiel du groupe Schiavone (fichiers de `cadrage/logo`, non modifiés
/// hormis le cadrage).
///
/// Le mot-symbole étant marine, le logo complet se pose toujours sur un fond
/// clair : sur un fond sombre, on l'affiche dans une plaque blanche arrondie.
class LogoSchiavone extends StatelessWidget {
  const LogoSchiavone({this.hauteur = 56, this.surPlaque = false, super.key});

  final double hauteur;

  /// Vrai pour entourer le logo d'une plaque blanche (fonds sombres).
  final bool surPlaque;

  @override
  Widget build(BuildContext context) {
    final logo = SvgPicture.asset(
      'assets/logo/schiavone-logo.svg',
      height: hauteur,
      semanticsLabel: 'Schiavone Group',
    );
    if (!surPlaque) return logo;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(Jetons.rayonBloc),
      ),
      child: logo,
    );
  }
}

/// Emblème seul (la façade du logo), lisible sur fond clair comme sur marine.
class EmblemeSchiavone extends StatelessWidget {
  const EmblemeSchiavone({this.largeur = 44, super.key});

  final double largeur;

  @override
  Widget build(BuildContext context) {
    return SvgPicture.asset(
      'assets/logo/schiavone-embleme.svg',
      width: largeur,
      excludeFromSemantics: true,
    );
  }
}

/// Emblème dans une tuile blanche arrondie : repère de marque des en-têtes.
class TuileEmbleme extends StatelessWidget {
  const TuileEmbleme({this.taille = 44, super.key});

  final double taille;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: taille,
      height: taille,
      alignment: Alignment.center,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(taille * 0.32),
      ),
      child: EmblemeSchiavone(largeur: taille * 0.72),
    );
  }
}
