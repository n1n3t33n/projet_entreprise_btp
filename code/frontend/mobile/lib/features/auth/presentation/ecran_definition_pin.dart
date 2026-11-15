import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:phosphor_flutter/phosphor_flutter.dart';

import '../../../components/en_tetes.dart';
import '../../../components/surfaces.dart';
import '../../../core/providers.dart';
import '../../../theme/animations.dart';
import '../../../theme/jetons.dart';
import '../../../theme/palette.dart';
import 'widgets/clavier_pin.dart';

/// Définition du PIN local après une connexion en ligne réussie (EF-AUT-03).
/// Deux temps : saisie puis confirmation, au clavier numérique.
class EcranDefinitionPin extends ConsumerStatefulWidget {
  const EcranDefinitionPin({super.key});

  @override
  ConsumerState<EcranDefinitionPin> createState() => _EcranDefinitionPinState();
}

class _EcranDefinitionPinState extends ConsumerState<EcranDefinitionPin> {
  String _premier = '';
  String _courant = '';
  bool _confirmation = false;
  bool _differents = false;
  bool _enCours = false;

  Future<void> _ajouter(String chiffre) async {
    if (_courant.length >= longueurPin || _enCours) return;
    setState(() {
      _courant += chiffre;
      _differents = false;
    });
    if (_courant.length < longueurPin) return;

    if (!_confirmation) {
      setState(() {
        _premier = _courant;
        _courant = '';
        _confirmation = true;
      });
      return;
    }
    if (_courant != _premier) {
      HapticFeedback.heavyImpact();
      setState(() {
        _differents = true;
        _premier = '';
        _courant = '';
        _confirmation = false;
      });
      return;
    }
    setState(() => _enCours = true);
    await ref.read(controleurAuthProvider.notifier).definirPin(_premier);
  }

  void _effacer() {
    if (_courant.isEmpty) return;
    setState(() => _courant = _courant.substring(0, _courant.length - 1));
  }

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final t = context.t;

    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (_, _) =>
          ref.read(controleurAuthProvider.notifier).annulerEnrolement(),
      child: Scaffold(
        appBar: BarreEcran(
          titre: t.definirCodeTitre,
          sousTitre: t.definirCodeSousTitre,
        ),
        body: SingleChildScrollView(
          padding: const EdgeInsets.all(Jetons.margeMobile),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Apparition(
                child: Carte(
                  padding: const EdgeInsets.symmetric(
                    horizontal: Jetons.espace3,
                    vertical: 22,
                  ),
                  child: Column(
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          _Etape(
                            numero: 1,
                            active: !_confirmation,
                            faite: _confirmation,
                          ),
                          Container(width: 36, height: 2, color: p.bordure),
                          _Etape(
                            numero: 2,
                            active: _confirmation,
                            faite: false,
                          ),
                        ],
                      ),
                      const SizedBox(height: Jetons.espace3),
                      AnimatedSwitcher(
                        duration: Jetons.dureeNormale,
                        switchInCurve: Jetons.courbe,
                        child: Column(
                          key: ValueKey(_confirmation),
                          children: [
                            Text(
                              _confirmation ? t.confirmerCode : t.choisirCode,
                              style: TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.w700,
                                color: p.sombre ? p.texte : Jetons.marine,
                              ),
                            ),
                            const SizedBox(height: 6),
                            Text(
                              _confirmation
                                  ? t.confirmerCodeAide
                                  : t.choisirCodeAide,
                              textAlign: TextAlign.center,
                              style: TextStyle(
                                color: p.texteSecondaire,
                                height: 1.35,
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: Jetons.espace4),
                      if (_enCours)
                        const SizedBox(
                          height: 18,
                          width: 18,
                          child: CircularProgressIndicator(strokeWidth: 2.5),
                        )
                      else
                        PointsPin(
                          remplis: _courant.length,
                          erreur: _differents,
                        ),
                      if (_differents) ...[
                        const SizedBox(height: 12),
                        Semantics(
                          liveRegion: true,
                          child: Text(
                            t.codesDifferents,
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              color: p.danger,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 12),
              Apparition(
                rang: 1,
                child: ClavierPin(
                  onChiffre: _ajouter,
                  onEffacer: _effacer,
                  onRaz: () => setState(() => _courant = ''),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _Etape extends StatelessWidget {
  const _Etape({
    required this.numero,
    required this.active,
    required this.faite,
  });

  final int numero;
  final bool active;
  final bool faite;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final plein = active || faite;
    return AnimatedContainer(
      duration: Jetons.dureeMicro,
      width: 30,
      height: 30,
      alignment: Alignment.center,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: faite ? p.succes : (active ? p.primaire : p.fondAlt),
      ),
      child: faite
          ? Icon(PhosphorIconsBold.check, size: 16, color: p.surface)
          : Text(
              '$numero',
              style: TextStyle(
                fontWeight: FontWeight.w800,
                color: plein ? p.surPrimaire : p.texteSecondaire,
              ),
            ),
    );
  }
}
