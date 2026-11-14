import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:phosphor_flutter/phosphor_flutter.dart';

import '../../../components/boutons.dart';
import '../../../components/logo_schiavone.dart';
import '../../../components/surfaces.dart';
import '../../../core/navigation/onglet_role.dart';
import '../../../core/providers.dart';
import '../../../core/roles/role_terrain.dart';
import '../../../theme/animations.dart';
import '../../../theme/jetons.dart';
import '../../../theme/palette.dart';
import '../domain/profil_utilisateur.dart';
import 'widgets/clavier_pin.dart';

/// Déverrouillage hors-ligne par PIN (session valide moins de 14 jours).
/// Reprend la maquette « Écran 1 — Connexion PIN hors-ligne ».
class EcranDeverrouillage extends ConsumerStatefulWidget {
  const EcranDeverrouillage({
    required this.profil,
    required this.role,
    this.derniereConnexion,
    super.key,
  });

  final ProfilUtilisateur profil;
  final RoleTerrain role;
  final DateTime? derniereConnexion;

  @override
  ConsumerState<EcranDeverrouillage> createState() =>
      _EcranDeverrouillageState();
}

class _EcranDeverrouillageState extends ConsumerState<EcranDeverrouillage> {
  String _pin = '';
  bool _erreur = false;
  bool _enCours = false;

  void _ajouter(String chiffre) {
    if (_pin.length >= longueurPin || _enCours) return;
    setState(() {
      _pin += chiffre;
      _erreur = false;
    });
    // Le sixième chiffre valide tout seul : un geste de moins sur le chantier.
    if (_pin.length == longueurPin) _connecter();
  }

  void _effacer() {
    if (_pin.isEmpty) return;
    setState(() {
      _pin = _pin.substring(0, _pin.length - 1);
      _erreur = false;
    });
  }

  void _raz() => setState(() {
    _pin = '';
    _erreur = false;
  });

  Future<void> _connecter() async {
    if (_pin.length < longueurPin) {
      setState(() => _erreur = true);
      return;
    }
    setState(() => _enCours = true);
    final ok = await ref
        .read(controleurAuthProvider.notifier)
        .deverrouiller(_pin);
    if (!mounted) return;
    if (!ok) HapticFeedback.heavyImpact();
    setState(() {
      _enCours = false;
      _erreur = !ok;
      if (!ok) _pin = '';
    });
  }

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final t = context.t;
    final incomplet = _erreur && _pin.isEmpty;

    return Scaffold(
      body: Column(
        children: [
          const _BanniereHorsLigne(),
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.fromLTRB(
                Jetons.margeMobile,
                Jetons.espace3,
                Jetons.margeMobile,
                Jetons.espace4,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const Apparition(child: _CarteMarque()),
                  const SizedBox(height: 12),
                  Apparition(
                    rang: 1,
                    child: _CarteOperateur(
                      profil: widget.profil,
                      role: widget.role,
                      onChanger: _confirmerChangement,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Apparition(
                    rang: 2,
                    child: Carte(
                      padding: const EdgeInsets.symmetric(
                        horizontal: Jetons.espace3,
                        vertical: 20,
                      ),
                      child: Column(
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(
                                PhosphorIconsRegular.password,
                                size: 18,
                                color: p.sombre ? p.texte : Jetons.marine,
                              ),
                              const SizedBox(width: 8),
                              Text(
                                t.pinTitre,
                                style: TextStyle(
                                  fontWeight: FontWeight.w800,
                                  letterSpacing: 0.6,
                                  color: p.sombre ? p.texte : Jetons.marine,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: Jetons.espace3),
                          PointsPin(remplis: _pin.length, erreur: _erreur),
                          const SizedBox(height: 12),
                          AnimatedSwitcher(
                            duration: Jetons.dureeMicro,
                            child: Text(
                              _erreur
                                  ? (incomplet
                                        ? t.pinIncorrect
                                        : t.pinIncomplet)
                                  : t.pinAide,
                              key: ValueKey('$_erreur$incomplet'),
                              style: TextStyle(
                                color: _erreur ? p.danger : p.texteSecondaire,
                                fontWeight: _erreur
                                    ? FontWeight.w700
                                    : FontWeight.w400,
                                fontSize: 13,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 10),
                  Apparition(
                    rang: 3,
                    child: ClavierPin(
                      onChiffre: _ajouter,
                      onEffacer: _effacer,
                      onRaz: _raz,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Apparition(
                    rang: 4,
                    child: _BandeauDeverrouillage(
                      derniereConnexion: widget.derniereConnexion,
                    ),
                  ),
                  const SizedBox(height: Jetons.espace3),
                  Apparition(
                    rang: 5,
                    child: BoutonPrincipal(
                      libelle: t.seConnecter,
                      iconeFin: PhosphorIconsBold.arrowRight,
                      enChargement: _enCours,
                      onPressed: _connecter,
                    ),
                  ),
                  const SizedBox(height: Jetons.espace3),
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          t.piedHorsLigne,
                          style: TextStyle(
                            color: p.texteSecondaire,
                            fontSize: 12,
                          ),
                        ),
                      ),
                      Pastille(
                        libelle: t.appareil(ref.watch(idAppareilProvider)),
                        icone: PhosphorIconsRegular.deviceMobile,
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _confirmerChangement() async {
    final t = context.t;
    final confirme = await showDialog<bool>(
      context: context,
      builder: (contexte) => AlertDialog(
        title: Text(t.retirerCompteTitre),
        content: Text(t.retirerCompteTexte),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(contexte).pop(false),
            child: Text(t.annuler),
          ),
          TextButton(
            onPressed: () => Navigator.of(contexte).pop(true),
            child: Text(t.retirerCompteAction),
          ),
        ],
      ),
    );
    if (confirme == true) {
      await ref.read(controleurAuthProvider.notifier).revoquer();
    }
  }
}

class _BanniereHorsLigne extends StatelessWidget {
  const _BanniereHorsLigne();

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    return AnnotatedRegion<SystemUiOverlayStyle>(
      value: SystemUiOverlayStyle.light,
      child: Container(
        width: double.infinity,
        decoration: BoxDecoration(
          gradient: LinearGradient(colors: [p.enteteDebut, p.enteteFin]),
        ),
        child: SafeArea(
          bottom: false,
          child: Padding(
            padding: const EdgeInsets.symmetric(
              horizontal: Jetons.espace3,
              vertical: 10,
            ),
            child: Row(
              children: [
                Container(
                  width: 8,
                  height: 8,
                  decoration: const BoxDecoration(
                    shape: BoxShape.circle,
                    color: Jetons.sable,
                  ),
                ),
                const SizedBox(width: 10),
                const Icon(
                  PhosphorIconsRegular.cloudSlash,
                  color: Colors.white,
                  size: 18,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    context.t.modeHorsLigneSecurise,
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.w700,
                      letterSpacing: 0.5,
                      fontSize: 13,
                    ),
                  ),
                ),
              ],
            ),
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
    final p = context.palette;
    return Carte(
      child: Row(
        children: [
          const TuileEmbleme(taille: 52),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'ChantierSync',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.w800,
                    color: p.sombre ? p.texte : Jetons.marine,
                  ),
                ),
                Text(
                  'Schiavone Group · Italia Construction',
                  style: TextStyle(color: p.texteSecondaire, fontSize: 12.5),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _CarteOperateur extends StatelessWidget {
  const _CarteOperateur({
    required this.profil,
    required this.role,
    required this.onChanger,
  });

  final ProfilUtilisateur profil;
  final RoleTerrain role;
  final VoidCallback onChanger;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final t = context.t;
    return Carte(
      child: Row(
        children: [
          AvatarInitiales(profil.nomComplet, taille: 48),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  profil.nomComplet,
                  style: TextStyle(
                    fontWeight: FontWeight.w700,
                    fontSize: 16,
                    color: p.texte,
                  ),
                ),
                Text(
                  '${libelleRole(t, role)} · ${profil.perimetre}',
                  style: TextStyle(color: p.texteSecondaire, fontSize: 12.5),
                ),
              ],
            ),
          ),
          const SizedBox(width: 8),
          BoutonSecondaire(
            libelle: t.changer,
            icone: PhosphorIconsRegular.swap,
            ton: Ton.neutre,
            compact: true,
            onPressed: onChanger,
          ),
        ],
      ),
    );
  }
}

class _BandeauDeverrouillage extends StatelessWidget {
  const _BandeauDeverrouillage({this.derniereConnexion});

  final DateTime? derniereConnexion;

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    final t = context.t;
    final date = derniereConnexion;
    final langue = Localizations.localeOf(context).toLanguageTag();
    return Bloc(
      couleur: p.succesFond,
      bordure: p.succes.withValues(alpha: 0.25),
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      child: Row(
        children: [
          Icon(PhosphorIconsFill.sealCheck, color: p.succes),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  t.deverrouillageActif,
                  style: TextStyle(
                    color: p.succes,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                Text(
                  date == null
                      ? t.donneesSurAppareil
                      : t.donneesSynchroniseesLe(
                          DateFormat.MMMd(langue).add_Hm().format(date),
                        ),
                  style: TextStyle(color: p.succes, fontSize: 12.5),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
