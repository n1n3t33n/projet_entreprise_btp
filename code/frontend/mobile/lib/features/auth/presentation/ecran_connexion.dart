import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:phosphor_flutter/phosphor_flutter.dart';

import '../../../core/providers.dart';
import '../../../theme/animations.dart';
import '../../../theme/jetons.dart';
import '../domain/etat_auth.dart';

/// Écran de connexion en ligne (première connexion ou reconnexion après
/// expiration du verrou de 14 jours). Reprend l'esthétique marine de la charte.
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
      backgroundColor: Jetons.fond,
      body: Column(
        children: [
          const _BanniereConnexion(),
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(Jetons.margeMobile),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const SizedBox(height: Jetons.espace4),
                  const Apparition(child: _CarteMarque()),
                  const SizedBox(height: Jetons.espace4),
                  Apparition(
                    delai: const Duration(milliseconds: 80),
                    child: _CarteIdentifiants(
                      identifiant: _identifiant,
                      motDePasse: _motDePasse,
                      onValider: _connecter,
                    ),
                  ),
                  if (message != null) ...[
                    const SizedBox(height: Jetons.espace3),
                    _Message(message),
                  ],
                  const SizedBox(height: Jetons.espace4),
                  Apparition(
                    delai: const Duration(milliseconds: 140),
                    child: FilledButton(
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
                  ),
                  const SizedBox(height: Jetons.espace3),
                  const Center(
                    child: Text(
                      'Connexion requise une fois, puis accès par code PIN.',
                      textAlign: TextAlign.center,
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

class _BanniereConnexion extends StatelessWidget {
  const _BanniereConnexion();

  @override
  Widget build(BuildContext context) {
    return const Material(
      color: Jetons.marine,
      child: SafeArea(
        bottom: false,
        child: Padding(
          padding: EdgeInsets.symmetric(
            horizontal: Jetons.espace3,
            vertical: Jetons.espace2,
          ),
          child: Row(
            children: [
              Icon(
                PhosphorIconsRegular.shieldCheck,
                color: Colors.white,
                size: 18,
              ),
              SizedBox(width: Jetons.espace2),
              Text(
                'CONNEXION SÉCURISÉE',
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
    return Column(
      children: [
        Container(
          width: 56,
          height: 56,
          alignment: Alignment.center,
          decoration: BoxDecoration(
            color: Jetons.marine,
            borderRadius: BorderRadius.circular(Jetons.rayonCarte),
          ),
          child: const Icon(
            PhosphorIconsRegular.buildings,
            color: Colors.white,
            size: 28,
          ),
        ),
        const SizedBox(height: Jetons.espace3),
        Text(
          'ChantierSync',
          style: Theme.of(context).textTheme.headlineSmall?.copyWith(
            color: Jetons.marine,
            fontWeight: FontWeight.w700,
          ),
        ),
        const SizedBox(height: 2),
        const Text(
          'Schiavone Group · Italia Construction',
          style: TextStyle(color: Jetons.texteSecondaire),
        ),
      ],
    );
  }
}

class _CarteIdentifiants extends StatelessWidget {
  const _CarteIdentifiants({
    required this.identifiant,
    required this.motDePasse,
    required this.onValider,
  });

  final TextEditingController identifiant;
  final TextEditingController motDePasse;
  final VoidCallback onValider;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(Jetons.espace3),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            TextField(
              controller: identifiant,
              decoration: const InputDecoration(
                labelText: 'Identifiant',
                prefixIcon: Icon(PhosphorIconsRegular.user),
              ),
              textInputAction: TextInputAction.next,
            ),
            const SizedBox(height: Jetons.espace3),
            TextField(
              controller: motDePasse,
              decoration: const InputDecoration(
                labelText: 'Mot de passe',
                prefixIcon: Icon(PhosphorIconsRegular.lockKey),
              ),
              obscureText: true,
              onSubmitted: (_) => onValider(),
            ),
          ],
        ),
      ),
    );
  }
}

class _Message extends StatelessWidget {
  const _Message(this.texte);

  final String texte;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(Jetons.espace3),
      decoration: BoxDecoration(
        color: const Color(0xFFFBEAE8),
        borderRadius: BorderRadius.circular(Jetons.rayonChamp),
        border: Border.all(color: const Color(0xFFE6B8B3)),
      ),
      child: Row(
        children: [
          const Icon(PhosphorIconsRegular.warning, color: Jetons.danger),
          const SizedBox(width: Jetons.espace2),
          Expanded(
            child: Text(texte, style: const TextStyle(color: Jetons.danger)),
          ),
        ],
      ),
    );
  }
}
