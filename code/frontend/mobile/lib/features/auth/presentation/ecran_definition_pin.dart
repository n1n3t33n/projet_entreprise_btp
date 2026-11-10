import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/providers.dart';
import '../../../theme/animations.dart';
import '../../../theme/jetons.dart';
import 'widgets/clavier_pin.dart';

/// Définition du PIN local après une connexion en ligne réussie (EF-AUT-03).
/// Deux temps : saisie puis confirmation, au clavier numérique.
class EcranDefinitionPin extends ConsumerStatefulWidget {
  const EcranDefinitionPin({super.key});

  @override
  ConsumerState<EcranDefinitionPin> createState() => _EcranDefinitionPinState();
}

enum _Phase { saisie, confirmation }

class _EcranDefinitionPinState extends ConsumerState<EcranDefinitionPin> {
  static const _longueur = 6;
  _Phase _phase = _Phase.saisie;
  String _premier = '';
  String _courant = '';
  String? _erreur;

  Future<void> _ajouter(String chiffre) async {
    if (_courant.length >= _longueur) return;
    setState(() {
      _courant += chiffre;
      _erreur = null;
    });
    if (_courant.length == _longueur) await _etapeComplete();
  }

  Future<void> _etapeComplete() async {
    if (_phase == _Phase.saisie) {
      setState(() {
        _premier = _courant;
        _courant = '';
        _phase = _Phase.confirmation;
      });
      return;
    }
    if (_courant != _premier) {
      setState(() {
        _erreur = 'Les deux codes ne correspondent pas.';
        _premier = '';
        _courant = '';
        _phase = _Phase.saisie;
      });
      return;
    }
    await ref.read(controleurAuthProvider.notifier).definirPin(_premier);
  }

  void _effacer() {
    if (_courant.isEmpty) return;
    setState(() => _courant = _courant.substring(0, _courant.length - 1));
  }

  void _raz() => setState(() => _courant = '');

  @override
  Widget build(BuildContext context) {
    final titre = _phase == _Phase.saisie
        ? 'Choisissez un code'
        : 'Confirmez le code';
    final sousTitre = _phase == _Phase.saisie
        ? 'Un code à 6 chiffres pour ouvrir l\'application sans réseau.'
        : 'Saisissez à nouveau le même code.';

    return Scaffold(
      backgroundColor: Jetons.fond,
      appBar: AppBar(title: const Text('Définir mon code')),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(Jetons.margeMobile),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Apparition(
                child: Card(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(
                      horizontal: Jetons.espace3,
                      vertical: Jetons.espace4,
                    ),
                    child: Column(
                      children: [
                        Text(
                          titre,
                          style: Theme.of(context).textTheme.titleMedium
                              ?.copyWith(
                                color: Jetons.marine,
                                fontWeight: FontWeight.w700,
                              ),
                        ),
                        const SizedBox(height: Jetons.espace2),
                        Text(
                          sousTitre,
                          textAlign: TextAlign.center,
                          style: const TextStyle(color: Jetons.texteSecondaire),
                        ),
                        const SizedBox(height: Jetons.espace4),
                        PointsPin(remplis: _courant.length, total: _longueur),
                      ],
                    ),
                  ),
                ),
              ),
              if (_erreur != null) ...[
                const SizedBox(height: Jetons.espace3),
                Text(
                  _erreur!,
                  textAlign: TextAlign.center,
                  style: const TextStyle(color: Jetons.danger),
                ),
              ],
              const SizedBox(height: Jetons.espace3),
              Apparition(
                delai: const Duration(milliseconds: 120),
                child: ClavierPin(
                  onChiffre: _ajouter,
                  onEffacer: _effacer,
                  onRaz: _raz,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
