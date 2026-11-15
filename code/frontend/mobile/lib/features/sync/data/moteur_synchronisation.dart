import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/providers.dart';
import '../../../core/stockage/magasin_documents.dart';
import '../domain/statut_envoi.dart';
import 'depot_file_envoi.dart';

/// Écart entre ce que l'appareil a saisi et ce que le serveur connaît.
class ConflitSynchronisation {
  const ConflitSynchronisation({
    required this.id,
    required this.article,
    required this.valeurAppareil,
    required this.valeurServeur,
  });

  factory ConflitSynchronisation.fromJson(Map<String, dynamic> j) =>
      ConflitSynchronisation(
        id: j['id'] as String,
        article: j['article'] as String,
        valeurAppareil: j['valeur_appareil'] as String,
        valeurServeur: j['valeur_serveur'] as String,
      );

  final String id;
  final String article;

  /// Ce que cet appareil a enregistré (« Sortie de 5 sac »).
  final String valeurAppareil;

  /// Ce que le serveur connaît (« Reste 4 sac »).
  final String valeurServeur;

  Map<String, dynamic> toJson() => {
    'id': id,
    'article': article,
    'valeur_appareil': valeurAppareil,
    'valeur_serveur': valeurServeur,
  };
}

/// Façon de résoudre un conflit.
enum ResolutionConflit {
  /// Le serveur fait foi : la saisie locale est ajustée.
  prioriteServeur,

  /// La saisie de terrain est conservée ; un stock négatif sera signalé.
  versionLocale,

  /// La décision est renvoyée au bureau.
  arbitrage,
}

/// État de la synchronisation de l'appareil.
class EtatSynchronisation {
  const EtatSynchronisation({required this.conflits, this.derniere});

  final DateTime? derniere;
  final List<ConflitSynchronisation> conflits;
}

/// Moteur de synchronisation.
///
/// Tant que le serveur n'existe pas, l'envoi est simulé : chaque événement en
/// attente est marqué accepté, exactement comme le fera la réponse du serveur.
/// L'envoi reste idempotent : relancer une synchronisation ne renvoie rien.
class MoteurSynchronisation {
  MoteurSynchronisation(
    this._documents,
    this._file, {
    DateTime Function()? horloge,
  }) : _horloge = horloge ?? DateTime.now;

  final MagasinDocuments _documents;
  final DepotFileEnvoi _file;
  final DateTime Function() _horloge;

  static const String _type = 'synchronisation';

  Future<EtatSynchronisation> etat() async {
    final brut = await _documents.lireObjet(_type, 'etat');
    if (brut == null) {
      return const EtatSynchronisation(
        conflits: [
          ConflitSynchronisation(
            id: 'conflit-cim-045',
            article: 'Ciment CPJ 45 — sac 50 kg',
            valeurAppareil: '5 sac',
            valeurServeur: '4 sac',
          ),
        ],
      );
    }
    return EtatSynchronisation(
      derniere: brut['derniere'] == null
          ? null
          : DateTime.parse(brut['derniere'] as String),
      conflits: [
        for (final c in (brut['conflits'] as List<dynamic>))
          ConflitSynchronisation.fromJson(c as Map<String, dynamic>),
      ],
    );
  }

  Future<void> _ecrire(EtatSynchronisation etat) =>
      _documents.ecrireObjet(_type, 'etat', {
        'derniere': etat.derniere?.toIso8601String(),
        'conflits': [for (final c in etat.conflits) c.toJson()],
      });

  /// Envoie les événements en attente. Renvoie le nombre d'événements envoyés.
  Future<int> synchroniser() async {
    final enAttente = (await _file.lister()).where((e) => e.enAttente).toList();
    for (final evenement in enAttente) {
      await _file.marquer(evenement.uuid, StatutEnvoi.accepte);
    }
    final courant = await etat();
    await _ecrire(
      EtatSynchronisation(derniere: _horloge(), conflits: courant.conflits),
    );
    return enAttente.length;
  }

  /// Applique la résolution choisie et retire le conflit de la liste.
  Future<void> resoudre(String idConflit, ResolutionConflit resolution) async {
    final courant = await etat();
    await _ecrire(
      EtatSynchronisation(
        derniere: courant.derniere,
        conflits: courant.conflits.where((c) => c.id != idConflit).toList(),
      ),
    );
    await _file.enfiler(
      uuid: 'resolution-$idConflit',
      type: 'RESOLUTION_CONFLIT',
      chargeUtile: {
        'id_conflit': idConflit,
        'resolution': resolution.name,
        'cree_le': _horloge().toIso8601String(),
        'resume': idConflit,
      },
    );
  }
}

final moteurSynchronisationProvider = Provider<MoteurSynchronisation>(
  (ref) => MoteurSynchronisation(
    ref.read(magasinDocumentsProvider),
    ref.read(depotFileEnvoiProvider),
  ),
);

final etatSynchronisationProvider = FutureProvider<EtatSynchronisation>(
  (ref) => ref.read(moteurSynchronisationProvider).etat(),
);
