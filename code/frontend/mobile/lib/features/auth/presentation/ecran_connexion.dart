import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:phosphor_flutter/phosphor_flutter.dart';

import '../../../components/boutons.dart';
import '../../../components/en_tetes.dart';
import '../../../components/logo_schiavone.dart';
import '../../../components/saisie.dart';
import '../../../components/surfaces.dart';
import '../../../core/config/env.dart';
import '../../../core/providers.dart';
import '../../../l10n/traductions.dart';
import '../../../theme/animations.dart';
import '../../../theme/jetons.dart';
import '../../../theme/palette.dart';
import '../data/service_auth.dart';
import '../domain/etat_auth.dart';

/// Texte affiché pour un motif de retour à l'écran de connexion.
String messageMotif(Traductions t, MotifConnexion motif, {int? secondes}) {
  return switch (motif) {
    MotifConnexion.identifiants => t.erreurIdentifiants,
    MotifConnexion.compteInactif => t.erreurCompteInactif,
    MotifConnexion.verrouille => t.erreurVerrouille(secondes ?? 0),
    MotifConnexion.sansAccesTerrain => t.erreurSansAccesTerrain,
    MotifConnexion.sessionRevoquee => t.infoSessionRevoquee,
    MotifConnexion.sessionExpiree => t.infoSessionExpiree,
    MotifConnexion.donneesInaccessibles => t.erreurDonneesInaccessibles,
    MotifConnexion.connexionImpossible => t.erreurConnexionImpossible,
  };
}

/// Écran de connexion en ligne (première connexion, ou reconnexion après
/// expiration du verrou de 14 jours). Aucune maquette mobile n'existe pour
/// cet écran : il prolonge l'écran PIN, dans la même identité.
class EcranConnexion extends ConsumerStatefulWidget {
  const EcranConnexion({super.key});

  @override
  ConsumerState<EcranConnexion> createState() => _EcranConnexionState();
}

class _EcranConnexionState extends ConsumerState<EcranConnexion> {
  final _identifiant = TextEditingController();
  final _motDePasse = TextEditingController();
  final _focusMotDePasse = FocusNode();
  bool _enCours = false;
  bool _masque = true;
  bool _identifiantVide = false;
  bool _motDePasseVide = false;

  @override
  void dispose() {
    _identifiant.dispose();
    _motDePasse.dispose();
    _focusMotDePasse.dispose();
    super.dispose();
  }

  Future<void> _connecter() async {
    final identifiant = _identifiant.text.trim();
    setState(() {
      _identifiantVide = identifiant.isEmpty;
      _motDePasseVide = _motDePasse.text.isEmpty;
    });
    if (_identifiantVide || _motDePasseVide || _enCours) return;

    setState(() => _enCours = true);
    await ref
        .read(controleurAuthProvider.notifier)
        .connexionEnLigne(identifiant, _motDePasse.text);
    if (mounted) setState(() => _enCours = false);
  }

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final t = context.t;
    final etat = ref.watch(controleurAuthProvider);
    final motif = etat is AuthNonConnecte ? etat.motif : null;
    final information =
        motif == MotifConnexion.sessionRevoquee ||
        motif == MotifConnexion.sessionExpiree;

    return Scaffold(
      body: AnnotatedRegion<SystemUiOverlayStyle>(
        value: SystemUiOverlayStyle.light,
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              FondFacade(
                rayonBas: 36,
                child: SafeArea(
                  bottom: false,
                  child: Padding(
                    padding: const EdgeInsets.fromLTRB(
                      Jetons.espace4,
                      Jetons.espace4,
                      Jetons.espace4,
                      Jetons.espace5,
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const LogoSchiavone(hauteur: 54, surPlaque: true),
                        const SizedBox(height: Jetons.espace4),
                        const Text(
                          'ChantierSync',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 30,
                            fontWeight: FontWeight.w800,
                            height: 1.1,
                          ),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          t.connexionAccroche,
                          style: const TextStyle(
                            color: Color(0xFFC9D9EA),
                            fontSize: 15,
                            height: 1.4,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
              Padding(
                padding: const EdgeInsets.all(Jetons.margeMobile),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    if (motif != null) ...[
                      Apparition(
                        child: _Message(
                          texte: messageMotif(
                            t,
                            motif,
                            secondes: etat is AuthNonConnecte
                                ? etat.secondesRestantes
                                : null,
                          ),
                          ton: information ? Ton.info : Ton.danger,
                        ),
                      ),
                      const SizedBox(height: 12),
                    ],
                    Apparition(
                      rang: 1,
                      child: Carte(
                        child: AutofillGroup(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.stretch,
                            children: [
                              LibelleChamp(t.identifiant, requis: true),
                              TextField(
                                controller: _identifiant,
                                autofillHints: const [AutofillHints.username],
                                textInputAction: TextInputAction.next,
                                autocorrect: false,
                                onSubmitted: (_) =>
                                    _focusMotDePasse.requestFocus(),
                                decoration: InputDecoration(
                                  prefixIcon: const Icon(
                                    PhosphorIconsRegular.user,
                                  ),
                                  errorText: _identifiantVide
                                      ? t.champObligatoire
                                      : null,
                                ),
                              ),
                              const SizedBox(height: Jetons.espace3),
                              LibelleChamp(t.motDePasse, requis: true),
                              TextField(
                                controller: _motDePasse,
                                focusNode: _focusMotDePasse,
                                autofillHints: const [AutofillHints.password],
                                obscureText: _masque,
                                onSubmitted: (_) => _connecter(),
                                decoration: InputDecoration(
                                  prefixIcon: const Icon(
                                    PhosphorIconsRegular.lockKey,
                                  ),
                                  errorText: _motDePasseVide
                                      ? t.champObligatoire
                                      : null,
                                  suffixIcon: IconButton(
                                    tooltip: _masque
                                        ? t.afficherMotDePasse
                                        : t.masquerMotDePasse,
                                    onPressed: () =>
                                        setState(() => _masque = !_masque),
                                    icon: Icon(
                                      _masque
                                          ? PhosphorIconsRegular.eye
                                          : PhosphorIconsRegular.eyeSlash,
                                    ),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: Jetons.espace3),
                    Apparition(
                      rang: 2,
                      child: BoutonPrincipal(
                        libelle: t.seConnecter,
                        iconeFin: PhosphorIconsBold.arrowRight,
                        enChargement: _enCours,
                        onPressed: _connecter,
                      ),
                    ),
                    const SizedBox(height: 12),
                    Text(
                      t.connexionAide,
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        color: p.texteSecondaire,
                        fontSize: 12.5,
                      ),
                    ),
                    if (Env.apiSimulee) ...[
                      const SizedBox(height: Jetons.espace4),
                      Apparition(
                        rang: 3,
                        child: _ComptesDemonstration(
                          onChoisir: (compte) {
                            _identifiant.text = compte.identifiant;
                            _motDePasse.text = 'demo';
                            setState(() {
                              _identifiantVide = false;
                              _motDePasseVide = false;
                            });
                          },
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _Message extends StatelessWidget {
  const _Message({required this.texte, required this.ton});

  final String texte;
  final Ton ton;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    return Semantics(
      liveRegion: true,
      child: Bloc(
        couleur: ton.fond(p),
        bordure: ton.texte(p).withValues(alpha: 0.3),
        padding: const EdgeInsets.all(14),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(
              ton == Ton.danger
                  ? PhosphorIconsRegular.warning
                  : PhosphorIconsRegular.info,
              color: ton.texte(p),
              size: 20,
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Text(
                texte,
                style: TextStyle(
                  color: ton.texte(p),
                  fontWeight: FontWeight.w600,
                  height: 1.35,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Comptes de démonstration : visibles uniquement tant que les données sont
/// simulées. Ils disparaissent dès que l'application parle au vrai serveur.
class _ComptesDemonstration extends StatelessWidget {
  const _ComptesDemonstration({required this.onChoisir});

  final void Function(CompteDemonstration compte) onChoisir;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final t = context.t;
    return Bloc(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            t.comptesDemoTitre,
            style: TextStyle(fontWeight: FontWeight.w700, color: p.texte),
          ),
          const SizedBox(height: 4),
          Text(
            t.comptesDemoAide,
            style: TextStyle(
              color: p.texteSecondaire,
              fontSize: 12.5,
              height: 1.35,
            ),
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              for (final compte in ServiceAuthSimule.comptes)
                PuceChoix(
                  libelle: compte.fonction,
                  selectionnee: false,
                  onTap: () => onChoisir(compte),
                ),
            ],
          ),
        ],
      ),
    );
  }
}
