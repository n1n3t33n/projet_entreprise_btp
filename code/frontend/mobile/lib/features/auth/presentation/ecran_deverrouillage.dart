import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/providers.dart';
import '../../../theme/jetons.dart';

/// Déverrouillage hors-ligne par PIN (session valide moins de 14 jours).
class EcranDeverrouillage extends ConsumerStatefulWidget {
  const EcranDeverrouillage({required this.identifiant, super.key});

  final String identifiant;

  @override
  ConsumerState<EcranDeverrouillage> createState() =>
      _EcranDeverrouillageState();
}

class _EcranDeverrouillageState extends ConsumerState<EcranDeverrouillage> {
  final _pin = TextEditingController();
  String? _erreur;
  bool _enCours = false;

  @override
  void dispose() {
    _pin.dispose();
    super.dispose();
  }

  Future<void> _deverrouiller() async {
    setState(() {
      _erreur = null;
      _enCours = true;
    });
    final ok = await ref
        .read(controleurAuthProvider.notifier)
        .deverrouiller(_pin.text);
    if (!mounted) return;
    setState(() {
      _enCours = false;
      if (!ok) _erreur = 'Code incorrect.';
    });
  }

  Future<void> _revoquer() =>
      ref.read(controleurAuthProvider.notifier).revoquer();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(Jetons.espace4),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                'Bonjour ${widget.identifiant}',
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: Jetons.espace2),
              const Text(
                'Saisissez votre code pour continuer.',
                textAlign: TextAlign.center,
                style: TextStyle(color: Jetons.texteSecondaire),
              ),
              const SizedBox(height: Jetons.espace4),
              TextField(
                controller: _pin,
                decoration: const InputDecoration(labelText: 'Code'),
                obscureText: true,
                keyboardType: TextInputType.number,
                inputFormatters: [
                  FilteringTextInputFormatter.digitsOnly,
                  LengthLimitingTextInputFormatter(8),
                ],
                onSubmitted: (_) => _deverrouiller(),
              ),
              if (_erreur != null) ...[
                const SizedBox(height: Jetons.espace3),
                Text(
                  _erreur!,
                  textAlign: TextAlign.center,
                  style: const TextStyle(color: Jetons.danger),
                ),
              ],
              const SizedBox(height: Jetons.espace4),
              FilledButton(
                onPressed: _enCours ? null : _deverrouiller,
                child: const Text('Déverrouiller'),
              ),
              const SizedBox(height: Jetons.espace2),
              TextButton(
                onPressed: _revoquer,
                child: const Text('Se déconnecter de cet appareil'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
