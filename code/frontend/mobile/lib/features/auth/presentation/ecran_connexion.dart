import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/providers.dart';
import '../../../theme/jetons.dart';
import '../domain/etat_auth.dart';

/// Écran de connexion en ligne (première connexion ou reconnexion après
/// expiration du verrou de 14 jours).
class EcranConnexion extends ConsumerStatefulWidget {
  const EcranConnexion({super.key});

  @override
  ConsumerState<EcranConnexion> createState() => _EcranConnexionState();
}

class _EcranConnexionState extends ConsumerState<EcranConnexion> {
  final _identifiant = TextEditingController();
  final _motDePasse = TextEditingController();
  bool _enCours = false;

  @override
  void dispose() {
    _identifiant.dispose();
    _motDePasse.dispose();
    super.dispose();
  }

  Future<void> _connecter() async {
    setState(() => _enCours = true);
    await ref
        .read(controleurAuthProvider.notifier)
        .connexionEnLigne(_identifiant.text.trim(), _motDePasse.text);
    if (mounted) setState(() => _enCours = false);
  }

  @override
  Widget build(BuildContext context) {
    final etat = ref.watch(controleurAuthProvider);
    final message = switch (etat) {
      AuthNonConnecte(:final message) => message,
      AuthVerrouExpire() =>
        'Votre session hors-ligne a expiré. Reconnectez-vous pour continuer.',
      _ => null,
    };

    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(Jetons.espace4),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                'ChantierSync',
                style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                  color: Jetons.marine,
                  fontWeight: FontWeight.w700,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: Jetons.espace2),
              const Text(
                'Connexion sécurisée',
                textAlign: TextAlign.center,
                style: TextStyle(color: Jetons.texteSecondaire),
              ),
              const SizedBox(height: Jetons.espace5),
              TextField(
                controller: _identifiant,
                decoration: const InputDecoration(labelText: 'Identifiant'),
                textInputAction: TextInputAction.next,
              ),
              const SizedBox(height: Jetons.espace3),
              TextField(
                controller: _motDePasse,
                decoration: const InputDecoration(labelText: 'Mot de passe'),
                obscureText: true,
                onSubmitted: (_) => _connecter(),
              ),
              if (message != null) ...[
                const SizedBox(height: Jetons.espace3),
                Text(
                  message,
                  style: const TextStyle(color: Jetons.danger),
                  textAlign: TextAlign.center,
                ),
              ],
              const SizedBox(height: Jetons.espace4),
              FilledButton(
                onPressed: _enCours ? null : _connecter,
                child: _enCours
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Text('Se connecter'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
