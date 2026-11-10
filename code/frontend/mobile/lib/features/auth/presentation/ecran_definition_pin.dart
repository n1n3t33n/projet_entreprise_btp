import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/providers.dart';
import '../../../theme/jetons.dart';

/// Définition du PIN local après une connexion en ligne réussie (EF-AUT-03).
class EcranDefinitionPin extends ConsumerStatefulWidget {
  const EcranDefinitionPin({super.key});

  @override
  ConsumerState<EcranDefinitionPin> createState() => _EcranDefinitionPinState();
}

class _EcranDefinitionPinState extends ConsumerState<EcranDefinitionPin> {
  final _pin = TextEditingController();
  final _confirmation = TextEditingController();
  String? _erreur;
  bool _enCours = false;

  static const _longueurMin = 4;

  @override
  void dispose() {
    _pin.dispose();
    _confirmation.dispose();
    super.dispose();
  }

  Future<void> _valider() async {
    if (_pin.text.length < _longueurMin) {
      setState(() => _erreur = 'Le code doit comporter au moins 4 chiffres.');
      return;
    }
    if (_pin.text != _confirmation.text) {
      setState(() => _erreur = 'Les deux codes ne correspondent pas.');
      return;
    }
    setState(() {
      _erreur = null;
      _enCours = true;
    });
    await ref.read(controleurAuthProvider.notifier).definirPin(_pin.text);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Définir mon code')),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(Jetons.espace4),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Text(
                'Choisissez un code pour ouvrir l\'application sans réseau.',
                style: TextStyle(color: Jetons.texteSecondaire),
              ),
              const SizedBox(height: Jetons.espace4),
              _ChampPin(controleur: _pin, libelle: 'Nouveau code'),
              const SizedBox(height: Jetons.espace3),
              _ChampPin(
                controleur: _confirmation,
                libelle: 'Confirmer le code',
              ),
              if (_erreur != null) ...[
                const SizedBox(height: Jetons.espace3),
                Text(_erreur!, style: const TextStyle(color: Jetons.danger)),
              ],
              const SizedBox(height: Jetons.espace4),
              FilledButton(
                onPressed: _enCours ? null : _valider,
                child: const Text('Valider'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ChampPin extends StatelessWidget {
  const _ChampPin({required this.controleur, required this.libelle});

  final TextEditingController controleur;
  final String libelle;

  @override
  Widget build(BuildContext context) {
    return TextField(
      controller: controleur,
      decoration: InputDecoration(labelText: libelle),
      obscureText: true,
      keyboardType: TextInputType.number,
      inputFormatters: [
        FilteringTextInputFormatter.digitsOnly,
        LengthLimitingTextInputFormatter(8),
      ],
    );
  }
}
