import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../core/providers.dart';
import '../features/auth/presentation/widgets/clavier_pin.dart';
import '../theme/jetons.dart';
import '../theme/palette.dart';

/// Demande le code PIN pour signer une décision (approbation d'une sortie,
/// visa d'une étape). Renvoie `true` si le code saisi est le bon.
///
/// La signature engage l'opérateur : elle reste une feuille modale, la seule
/// de l'application à interrompre volontairement le geste en cours.
Future<bool> demanderSignaturePin(
  BuildContext context, {
  required String objet,
}) async {
  final signe = await showModalBottomSheet<bool>(
    context: context,
    isScrollControlled: true,
    builder: (_) => _FeuillePin(objet: objet),
  );
  return signe ?? false;
}

class _FeuillePin extends ConsumerStatefulWidget {
  const _FeuillePin({required this.objet});

  final String objet;

  @override
  ConsumerState<_FeuillePin> createState() => _FeuillePinState();
}

class _FeuillePinState extends ConsumerState<_FeuillePin> {
  String _pin = '';
  bool _erreur = false;
  bool _enCours = false;

  Future<void> _ajouter(String chiffre) async {
    if (_pin.length >= longueurPin || _enCours) return;
    setState(() {
      _pin += chiffre;
      _erreur = false;
    });
    if (_pin.length < longueurPin) return;

    setState(() => _enCours = true);
    final ok = await ref
        .read(controleurAuthProvider.notifier)
        .verifierPin(_pin);
    if (!mounted) return;
    if (ok) {
      Navigator.of(context).pop(true);
      return;
    }
    HapticFeedback.heavyImpact();
    setState(() {
      _enCours = false;
      _erreur = true;
      _pin = '';
    });
  }

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final t = context.t;
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(
          Jetons.espace3,
          0,
          Jetons.espace3,
          Jetons.espace3,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              t.signatureTitre,
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w700,
                color: p.sombre ? p.texte : Jetons.marine,
              ),
            ),
            const SizedBox(height: 6),
            Text(
              widget.objet,
              textAlign: TextAlign.center,
              style: TextStyle(color: p.texteSecondaire, height: 1.35),
            ),
            const SizedBox(height: Jetons.espace4),
            PointsPin(remplis: _pin.length, erreur: _erreur),
            const SizedBox(height: 10),
            Text(
              _erreur ? t.pinIncorrect : t.signatureAide,
              style: TextStyle(
                color: _erreur ? p.danger : p.texteSecondaire,
                fontWeight: _erreur ? FontWeight.w700 : FontWeight.w400,
                fontSize: 13,
              ),
            ),
            const SizedBox(height: Jetons.espace3),
            ClavierPin(
              onChiffre: _ajouter,
              onEffacer: () {
                if (_pin.isNotEmpty) {
                  setState(() => _pin = _pin.substring(0, _pin.length - 1));
                }
              },
              onRaz: () => setState(() => _pin = ''),
            ),
          ],
        ),
      ),
    );
  }
}
