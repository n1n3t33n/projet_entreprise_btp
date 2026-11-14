import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:phosphor_flutter/phosphor_flutter.dart';

import '../theme/jetons.dart';
import '../theme/palette.dart';
import 'boutons.dart';
import 'logo_schiavone.dart';

/// Fond marine des en-têtes : léger dégradé et motif « façade » repris de
/// l'emblème Schiavone (panneaux vitrés en perspective), très discret.
class FondFacade extends StatelessWidget {
  const FondFacade({
    required this.child,
    this.rayonBas = Jetons.rayonCarte + 4,
    super.key,
  });

  final Widget child;
  final double rayonBas;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    return AnnotatedRegion<SystemUiOverlayStyle>(
      value: SystemUiOverlayStyle.light,
      child: ClipRRect(
        borderRadius: BorderRadius.vertical(bottom: Radius.circular(rayonBas)),
        child: DecoratedBox(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [p.enteteDebut, p.enteteFin],
            ),
          ),
          child: CustomPaint(painter: const _MotifFacade(), child: child),
        ),
      ),
    );
  }
}

class _MotifFacade extends CustomPainter {
  const _MotifFacade();

  @override
  void paint(Canvas canvas, Size size) {
    final l = size.width;
    final h = size.height;
    final ciel = Paint()..color = Jetons.ciel.withValues(alpha: 0.10);
    final sable = Paint()..color = Jetons.sable.withValues(alpha: 0.09);

    // Panneau haut (ciel), en perspective comme sur l'emblème.
    canvas.drawPath(
      Path()
        ..moveTo(l * 0.58, h * 0.30)
        ..lineTo(l * 0.80, h * 0.08)
        ..lineTo(l * 0.80, h * 0.42)
        ..lineTo(l * 0.58, h * 0.50)
        ..close(),
      ciel,
    );
    // Panneau bas (sable).
    canvas.drawPath(
      Path()
        ..moveTo(l * 0.58, h * 0.55)
        ..lineTo(l * 0.80, h * 0.47)
        ..lineTo(l * 0.80, h * 0.82)
        ..lineTo(l * 0.58, h * 0.82)
        ..close(),
      sable,
    );
    // Vitrages de droite.
    canvas.drawRect(
      Rect.fromLTRB(l * 0.86, h * 0.08, l * 1.02, h * 0.42),
      ciel,
    );
    canvas.drawRect(
      Rect.fromLTRB(l * 0.86, h * 0.47, l * 1.02, h * 0.82),
      sable,
    );
  }

  @override
  bool shouldRepaint(covariant CustomPainter ancien) => false;
}

/// En-tête des tableaux de bord : marque, chantier, rôle et opérateur.
class EnTeteRole extends StatelessWidget {
  const EnTeteRole({
    required this.surTitre,
    required this.titre,
    this.sousTitre,
    this.actions = const [],
    super.key,
  });

  /// Ligne de contexte (« SCHIAVONE GROUP · Chantier de Grand-Bassam »).
  final String surTitre;

  /// Ligne principale (« Magasinier · Mamadou Koné »).
  final String titre;
  final String? sousTitre;
  final List<Widget> actions;

  @override
  Widget build(BuildContext context) {
    return FondFacade(
      child: SafeArea(
        bottom: false,
        child: Padding(
          padding: const EdgeInsets.fromLTRB(
            Jetons.espace3,
            10,
            Jetons.espace3,
            18,
          ),
          child: Row(
            children: [
              const TuileEmbleme(),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      surTitre,
                      style: const TextStyle(
                        color: Jetons.ciel,
                        fontSize: 11.5,
                        fontWeight: FontWeight.w700,
                        letterSpacing: 0.4,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      titre,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 17,
                        fontWeight: FontWeight.w700,
                        height: 1.2,
                      ),
                    ),
                    if (sousTitre != null) ...[
                      const SizedBox(height: 2),
                      Text(
                        sousTitre!,
                        style: const TextStyle(
                          color: Color(0xFFC9D9EA),
                          fontSize: 12.5,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
              for (final action in actions) ...[
                const SizedBox(width: 8),
                action,
              ],
            ],
          ),
        ),
      ),
    );
  }
}

/// Barre haute des écrans ouverts depuis un tableau de bord : retour, titre,
/// contexte et actions.
class BarreEcran extends StatelessWidget implements PreferredSizeWidget {
  const BarreEcran({
    required this.titre,
    this.sousTitre,
    this.actions = const [],
    super.key,
  });

  final String titre;
  final String? sousTitre;
  final List<Widget> actions;

  @override
  Size get preferredSize => const Size.fromHeight(68);

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final peutRevenir = Navigator.of(context).canPop();
    return AnnotatedRegion<SystemUiOverlayStyle>(
      value: p.sombre ? SystemUiOverlayStyle.light : SystemUiOverlayStyle.dark,
      child: Container(
        decoration: BoxDecoration(
          color: p.surface,
          border: Border(bottom: BorderSide(color: p.bordure)),
        ),
        child: SafeArea(
          bottom: false,
          child: SizedBox(
            height: 68,
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 12),
              child: Row(
                children: [
                  if (peutRevenir) ...[
                    BoutonIcone(
                      icone: PhosphorIconsRegular.arrowLeft,
                      libelle: MaterialLocalizations.of(
                        context,
                      ).backButtonTooltip,
                      onPressed: () => Navigator.of(context).maybePop(),
                    ),
                    const SizedBox(width: 10),
                  ] else
                    const SizedBox(width: 4),
                  Expanded(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          titre,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.w700,
                            color: p.sombre ? p.texte : Jetons.marine,
                          ),
                        ),
                        if (sousTitre != null)
                          Text(
                            sousTitre!,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: TextStyle(
                              fontSize: 12.5,
                              color: p.texteSecondaire,
                            ),
                          ),
                      ],
                    ),
                  ),
                  for (final action in actions) ...[
                    const SizedBox(width: 8),
                    action,
                  ],
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
