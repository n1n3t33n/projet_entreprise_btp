import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:phosphor_flutter/phosphor_flutter.dart';

import '../../../core/navigation/acces_par_role.dart';
import '../../../core/navigation/ecran_mobile.dart';
import '../../../core/providers.dart';
import '../../../core/roles/role_terrain.dart';
import '../../../theme/animations.dart';
import '../../../theme/jetons.dart';

/// Accueil dédié au rôle (wireframes A1–A5). Expose, en tuiles, les fonctions
/// autorisées au rôle, avec le bandeau de synchronisation et l'action
/// principale propre au métier. Les écrans métier non livrés en M1 sont
/// clairement marqués « prochain jalon ».
class AccueilRole extends ConsumerWidget {
  const AccueilRole({
    required this.role,
    required this.onNaviguer,
    required this.onSynchroniser,
    super.key,
  });

  final RoleTerrain role;
  final void Function(EcranMobile ecran) onNaviguer;
  final VoidCallback onSynchroniser;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final ecrans = AccesParRole.ecransAutorises(role);
    final raccourcis = ecrans
        .where(
          (e) => e != EcranMobile.accueil && e != EcranMobile.synchronisation,
        )
        .toList();
    final action = _actionPrincipale(role, raccourcis);

    return ListView(
      padding: const EdgeInsets.all(Jetons.margeMobile),
      children: [
        Apparition(
          child: _BanniereSynchro(
            enAttente: ref.read(depotFileEnvoiProvider).compterEnAttente(),
            onSynchroniser: onSynchroniser,
          ),
        ),
        const SizedBox(height: Jetons.espace4),
        const Apparition(
          delai: Duration(milliseconds: 60),
          child: _TitreSection('Mes actions'),
        ),
        const SizedBox(height: Jetons.espace3),
        for (var i = 0; i < raccourcis.length; i++) ...[
          Apparition(
            delai: Duration(milliseconds: 120 + i * 60),
            child: _TuileFonction(
              fonction: raccourcis[i],
              onTap: () => onNaviguer(raccourcis[i]),
            ),
          ),
          const SizedBox(height: Jetons.espace3),
        ],
        const SizedBox(height: Jetons.espace2),
        Apparition(
          delai: Duration(milliseconds: 120 + raccourcis.length * 60),
          child: const _ApercuChantier(),
        ),
        if (action != null) ...[
          const SizedBox(height: Jetons.espace4),
          Apparition(
            delai: Duration(milliseconds: 180 + raccourcis.length * 60),
            child: FilledButton.icon(
              onPressed: () => onNaviguer(action.cible),
              icon: const Icon(PhosphorIconsRegular.plus, size: 18),
              label: Text(action.libelle),
            ),
          ),
        ],
      ],
    );
  }

  /// Action principale (bouton marine) selon le métier du rôle. La cible est le
  /// premier écran métier autorisé (encore réservé en M1).
  ({String libelle, EcranMobile cible})? _actionPrincipale(
    RoleTerrain role,
    List<EcranMobile> raccourcis,
  ) {
    if (raccourcis.isEmpty) return null;
    final libelle = switch (role) {
      RoleTerrain.magasinier ||
      RoleTerrain.gestionnaireStock => 'NOUVEAU MOUVEMENT',
      RoleTerrain.technicien => 'NOUVELLE SAISIE',
      RoleTerrain.chefChantier ||
      RoleTerrain.responsableTechnique => 'NOUVELLE VALIDATION',
    };
    return (libelle: libelle, cible: raccourcis.first);
  }
}

/// Bandeau ambre : éléments en attente d'envoi + accès au centre de synchro.
class _BanniereSynchro extends StatelessWidget {
  const _BanniereSynchro({
    required this.enAttente,
    required this.onSynchroniser,
  });

  final Future<int> enAttente;
  final VoidCallback onSynchroniser;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(Jetons.espace3),
      decoration: BoxDecoration(
        color: Jetons.orClair,
        borderRadius: BorderRadius.circular(Jetons.rayonCarte),
        border: Border.all(color: Jetons.orVif),
      ),
      child: Row(
        children: [
          const Icon(PhosphorIconsRegular.cloudArrowUp, color: Jetons.or),
          const SizedBox(width: Jetons.espace3),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                FutureBuilder<int>(
                  future: enAttente,
                  builder: (context, snapshot) {
                    final nombre = snapshot.data ?? 0;
                    final texte = nombre == 0
                        ? 'Aucun élément en attente'
                        : 'En attente de $nombre élément'
                              '${nombre > 1 ? 's' : ''}';
                    return Text(
                      texte,
                      style: const TextStyle(
                        color: Jetons.or,
                        fontWeight: FontWeight.w700,
                      ),
                    );
                  },
                ),
                const SizedBox(height: 2),
                const Text(
                  'Données sécurisées sur l\'appareil',
                  style: TextStyle(color: Jetons.or, fontSize: 12),
                ),
              ],
            ),
          ),
          const SizedBox(width: Jetons.espace2),
          TextButton.icon(
            onPressed: onSynchroniser,
            icon: const Icon(PhosphorIconsRegular.arrowsClockwise, size: 16),
            label: const Text('Synchroniser'),
            style: TextButton.styleFrom(foregroundColor: Jetons.or),
          ),
        ],
      ),
    );
  }
}

class _TitreSection extends StatelessWidget {
  const _TitreSection(this.texte);

  final String texte;

  @override
  Widget build(BuildContext context) {
    return Text(
      texte,
      style: Theme.of(context).textTheme.titleMedium?.copyWith(
        color: Jetons.marine,
        fontWeight: FontWeight.w700,
      ),
    );
  }
}

class _TuileFonction extends StatelessWidget {
  const _TuileFonction({required this.fonction, required this.onTap});

  final EcranMobile fonction;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return CarteLevitation(
      onTap: onTap,
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(Jetons.espace3),
          child: Row(
            children: [
              Container(
                width: 44,
                height: 44,
                alignment: Alignment.center,
                decoration: BoxDecoration(
                  color: Jetons.fondSection,
                  borderRadius: BorderRadius.circular(Jetons.rayonChamp),
                ),
                child: Icon(fonction.icone, color: Jetons.sarcelle),
              ),
              const SizedBox(width: Jetons.espace3),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      fonction.libelle,
                      style: const TextStyle(
                        fontWeight: FontWeight.w700,
                        fontSize: 15,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      fonction.reserveJalonSuivant
                          ? 'Disponible au prochain jalon'
                          : 'Disponible',
                      style: const TextStyle(
                        color: Jetons.texteSecondaire,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
              if (fonction.reserveJalonSuivant)
                const _BadgeBientot()
              else
                const Icon(
                  PhosphorIconsRegular.caretRight,
                  color: Jetons.texteAttenue,
                ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Aperçu du chantier : structure du tableau de bord, chiffres à venir avec les
/// écrans métier (M2/M3). On n'affiche aucune valeur fabriquée.
class _ApercuChantier extends StatelessWidget {
  const _ApercuChantier();

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(Jetons.espace3),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(
                  PhosphorIconsRegular.chartBar,
                  size: 18,
                  color: Jetons.marine,
                ),
                const SizedBox(width: Jetons.espace2),
                Text(
                  'Aperçu du chantier',
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    color: Jetons.marine,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ],
            ),
            const SizedBox(height: Jetons.espace3),
            const Row(
              children: [
                Expanded(child: _StatVide(libelle: 'Références')),
                SizedBox(width: Jetons.espace3),
                Expanded(child: _StatVide(libelle: 'Alertes de seuil')),
              ],
            ),
            const SizedBox(height: Jetons.espace2),
            const Text(
              'Chiffres disponibles au prochain jalon.',
              style: TextStyle(color: Jetons.texteAttenue, fontSize: 12),
            ),
          ],
        ),
      ),
    );
  }
}

class _StatVide extends StatelessWidget {
  const _StatVide({required this.libelle});

  final String libelle;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(Jetons.espace3),
      decoration: BoxDecoration(
        color: Jetons.fond,
        borderRadius: BorderRadius.circular(Jetons.rayonChamp),
        border: Border.all(color: Jetons.bordure),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '—',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.w700,
              color: Jetons.marine,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            libelle,
            style: const TextStyle(color: Jetons.texteSecondaire, fontSize: 12),
          ),
        ],
      ),
    );
  }
}

class _BadgeBientot extends StatelessWidget {
  const _BadgeBientot();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: Jetons.espace2,
        vertical: 4,
      ),
      decoration: BoxDecoration(
        color: Jetons.orClair,
        borderRadius: BorderRadius.circular(999),
      ),
      child: const Text(
        'Bientôt',
        style: TextStyle(color: Jetons.or, fontSize: 12),
      ),
    );
  }
}
