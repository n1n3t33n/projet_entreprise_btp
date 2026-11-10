import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:phosphor_flutter/phosphor_flutter.dart';

import '../../../core/providers.dart';
import '../../../theme/animations.dart';
import '../../../theme/jetons.dart';
import 'widgets/clavier_pin.dart';

/// Déverrouillage hors-ligne par PIN (session valide moins de 14 jours).
/// Fidèle au wireframe « Écran 1 — Connexion PIN hors-ligne ».
class EcranDeverrouillage extends ConsumerStatefulWidget {
  const EcranDeverrouillage({required this.identifiant, super.key});

  final String identifiant;

  @override
  ConsumerState<EcranDeverrouillage> createState() =>
      _EcranDeverrouillageState();
}

class _EcranDeverrouillageState extends ConsumerState<EcranDeverrouillage> {
  static const _longueur = 6;
  String _pin = '';
  String? _erreur;
  bool _enCours = false;

  void _ajouter(String chiffre) {
    if (_pin.length >= _longueur) return;
    setState(() {
      _pin += chiffre;
      _erreur = null;
    });
  }

  void _effacer() {
    if (_pin.isEmpty) return;
    setState(() => _pin = _pin.substring(0, _pin.length - 1));
  }

  void _raz() => setState(() => _pin = '');

  Future<void> _connecter() async {
    if (_pin.length < 4) {
      setState(() => _erreur = 'Code incomplet.');
      return;
    }
    setState(() {
      _enCours = true;
      _erreur = null;
    });
    final ok = await ref
        .read(controleurAuthProvider.notifier)
        .deverrouiller(_pin);
    if (!mounted) return;
    setState(() {
      _enCours = false;
      if (!ok) {
        _erreur = 'Code incorrect.';
        _pin = '';
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Jetons.fond,
      body: Column(
        children: [
          const _BanniereHorsLigne(),
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(Jetons.margeMobile),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const Apparition(child: _CarteMarque()),
                  const SizedBox(height: Jetons.espace3),
                  Apparition(
                    delai: const Duration(milliseconds: 60),
                    child: _CarteOperateur(
                      identifiant: widget.identifiant,
                      onChanger: () =>
                          ref.read(controleurAuthProvider.notifier).revoquer(),
                    ),
                  ),
                  const SizedBox(height: Jetons.espace3),
                  Apparition(
                    delai: const Duration(milliseconds: 120),
                    child: _CartePin(remplis: _pin.length, total: _longueur),
                  ),
                  const SizedBox(height: Jetons.espace3),
                  Apparition(
                    delai: const Duration(milliseconds: 180),
                    child: ClavierPin(
                      onChiffre: _ajouter,
                      onEffacer: _effacer,
                      onRaz: _raz,
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
                  const Apparition(
                    delai: Duration(milliseconds: 240),
                    child: _BandeauDeverrouillage(),
                  ),
                  const SizedBox(height: Jetons.espace3),
                  FilledButton(
                    onPressed: _enCours ? null : _connecter,
                    child: _enCours
                        ? const SizedBox(
                            height: 20,
                            width: 20,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Text('SE CONNECTER'),
                              SizedBox(width: Jetons.espace2),
                              Icon(PhosphorIconsRegular.arrowRight, size: 18),
                            ],
                          ),
                  ),
                  const SizedBox(height: Jetons.espace2),
                  const Center(
                    child: Text(
                      'Stockage local sécurisé · Schiavone Group',
                      style: TextStyle(
                        color: Jetons.texteAttenue,
                        fontSize: 12,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _BanniereHorsLigne extends StatelessWidget {
  const _BanniereHorsLigne();

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Jetons.marine,
      child: SafeArea(
        bottom: false,
        child: Padding(
          padding: const EdgeInsets.symmetric(
            horizontal: Jetons.espace3,
            vertical: Jetons.espace2,
          ),
          child: Row(
            children: [
              Container(
                width: 8,
                height: 8,
                decoration: const BoxDecoration(
                  shape: BoxShape.circle,
                  color: Jetons.orVif,
                ),
              ),
              const SizedBox(width: Jetons.espace2),
              const Icon(
                PhosphorIconsRegular.cloudSlash,
                color: Colors.white,
                size: 18,
              ),
              const SizedBox(width: Jetons.espace2),
              const Text(
                'MODE HORS-LIGNE SÉCURISÉ',
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.w700,
                  letterSpacing: 0.5,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _CarteMarque extends StatelessWidget {
  const _CarteMarque();

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(Jetons.espace3),
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'ChantierSync',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      color: Jetons.marine,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const Text(
                    'Schiavone Group · Italia Construction',
                    style: TextStyle(color: Jetons.texteSecondaire),
                  ),
                ],
              ),
            ),
            Container(
              padding: const EdgeInsets.symmetric(
                horizontal: Jetons.espace2,
                vertical: 4,
              ),
              decoration: BoxDecoration(
                color: Jetons.fondSection,
                borderRadius: BorderRadius.circular(999),
              ),
              child: const Text(
                '● BTP · PRO',
                style: TextStyle(color: Jetons.sarcelle, fontSize: 12),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _CarteOperateur extends StatelessWidget {
  const _CarteOperateur({required this.identifiant, required this.onChanger});

  final String identifiant;
  final VoidCallback onChanger;

  @override
  Widget build(BuildContext context) {
    final initiales = identifiant.isEmpty
        ? '?'
        : identifiant.substring(0, 1).toUpperCase();
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(Jetons.espace3),
        child: Row(
          children: [
            CircleAvatar(
              radius: 24,
              backgroundColor: Jetons.marine,
              child: Text(
                initiales,
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
            const SizedBox(width: Jetons.espace3),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'OPÉRATEUR TERRAIN',
                    style: TextStyle(
                      color: Jetons.texteAttenue,
                      fontSize: 11,
                      fontWeight: FontWeight.w600,
                      letterSpacing: 0.5,
                    ),
                  ),
                  Text(
                    identifiant,
                    style: const TextStyle(
                      fontWeight: FontWeight.w700,
                      fontSize: 16,
                    ),
                  ),
                ],
              ),
            ),
            TextButton(onPressed: onChanger, child: const Text('Changer')),
          ],
        ),
      ),
    );
  }
}

class _CartePin extends StatelessWidget {
  const _CartePin({required this.remplis, required this.total});

  final int remplis;
  final int total;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.symmetric(
          horizontal: Jetons.espace3,
          vertical: Jetons.espace4,
        ),
        child: Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(
                  PhosphorIconsRegular.keyboard,
                  size: 18,
                  color: Jetons.marine,
                ),
                const SizedBox(width: Jetons.espace2),
                Text(
                  'CODE PIN CHANTIER',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color: Jetons.marine,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 0.5,
                  ),
                ),
              ],
            ),
            const SizedBox(height: Jetons.espace3),
            PointsPin(remplis: remplis, total: total),
            const SizedBox(height: Jetons.espace2),
            const Text(
              'Matricule déchiffré · 6 chiffres requis',
              style: TextStyle(color: Jetons.texteSecondaire),
            ),
          ],
        ),
      ),
    );
  }
}

class _BandeauDeverrouillage extends StatelessWidget {
  const _BandeauDeverrouillage();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(Jetons.espace3),
      decoration: BoxDecoration(
        color: const Color(0xFFE8F5E9),
        borderRadius: BorderRadius.circular(Jetons.rayonChamp),
        border: Border.all(color: const Color(0xFFBFE3C4)),
      ),
      child: const Row(
        children: [
          Icon(PhosphorIconsRegular.sealCheck, color: Jetons.succes),
          SizedBox(width: Jetons.espace3),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Déverrouillage hors-ligne actif',
                  style: TextStyle(
                    color: Jetons.succes,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                Text(
                  'Données sécurisées sur l\'appareil.',
                  style: TextStyle(color: Jetons.succes),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
