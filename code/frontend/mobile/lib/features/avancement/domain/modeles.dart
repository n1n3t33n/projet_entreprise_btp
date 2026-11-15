// Modèle de l'avancement des travaux côté terrain (CL-5, ET-1). Mêmes statuts
// que le poste de pilotage web : à faire, en cours, terminée déclarée,
// validée, bloquée.

/// Statut d'une étape de travaux (ET-1).
enum StatutEtape {
  aFaire('A_FAIRE'),
  enCours('EN_COURS'),
  termineeDeclaree('TERMINEE_DECLAREE'),
  validee('VALIDEE'),
  bloquee('BLOQUEE');

  const StatutEtape(this.code);

  final String code;

  static StatutEtape parCode(String code) =>
      values.firstWhere((s) => s.code == code, orElse: () => aFaire);
}

/// Nature d'un blocage de terrain. `ruptureMateriau` impose de désigner
/// l'article manquant (RG-A10).
enum NatureBlocage {
  ruptureMateriau,
  panneEngin,
  intemperies,
  nonConformite,
  accesBloque,
}

enum GraviteBlocage { arretTotal, ralenti, alerte }

enum RetardEstime { deuxHeures, demiJournee, unJourEtPlus }

class Blocage {
  const Blocage({
    required this.nature,
    required this.gravite,
    required this.retard,
    required this.date,
    this.observations,
    this.codeArticle,
    this.designationArticle,
  });

  factory Blocage.fromJson(Map<String, dynamic> j) => Blocage(
    nature: NatureBlocage.values.byName(j['nature'] as String),
    gravite: GraviteBlocage.values.byName(j['gravite'] as String),
    retard: RetardEstime.values.byName(j['retard'] as String),
    date: DateTime.parse(j['date'] as String),
    observations: j['observations'] as String?,
    codeArticle: j['code_article'] as String?,
    designationArticle: j['designation_article'] as String?,
  );

  final NatureBlocage nature;
  final GraviteBlocage gravite;
  final RetardEstime retard;
  final DateTime date;
  final String? observations;

  /// Article manquant, obligatoire pour une rupture de matériau.
  final String? codeArticle;
  final String? designationArticle;

  Map<String, dynamic> toJson() => {
    'nature': nature.name,
    'gravite': gravite.name,
    'retard': retard.name,
    'date': date.toIso8601String(),
    'observations': observations,
    'code_article': codeArticle,
    'designation_article': designationArticle,
  };
}

/// Étape de travaux d'une fiche de route.
class EtapeTravaux {
  const EtapeTravaux({
    required this.id,
    required this.libelle,
    required this.detail,
    required this.corpsEtat,
    required this.zone,
    required this.statut,
    required this.equipe,
    required this.idResponsable,
    required this.nomResponsable,
    required this.metreCible,
    required this.metreFait,
    required this.uniteMetre,
    required this.controles,
    required this.controlesFaits,
    required this.controleRequis,
    required this.secondesPointees,
    this.horaire,
    this.debutPointage,
    this.idAuteurDeclaration,
    this.nomAuteurDeclaration,
    this.blocage,
  });

  factory EtapeTravaux.fromJson(Map<String, dynamic> j) => EtapeTravaux(
    id: j['id'] as String,
    libelle: j['libelle'] as String,
    detail: j['detail'] as String,
    corpsEtat: j['corps_etat'] as String,
    zone: j['zone'] as String,
    statut: StatutEtape.parCode(j['statut'] as String),
    equipe: j['equipe'] as String,
    idResponsable: j['id_responsable'] as String,
    nomResponsable: j['nom_responsable'] as String,
    metreCible: j['metre_cible'] as num,
    metreFait: j['metre_fait'] as num,
    uniteMetre: j['unite_metre'] as String,
    controles: (j['controles'] as List<dynamic>).cast<String>(),
    controlesFaits: (j['controles_faits'] as List<dynamic>).cast<bool>(),
    controleRequis: j['controle_requis'] as bool,
    secondesPointees: j['secondes_pointees'] as int,
    horaire: j['horaire'] as String?,
    debutPointage: j['debut_pointage'] == null
        ? null
        : DateTime.parse(j['debut_pointage'] as String),
    idAuteurDeclaration: j['id_auteur_declaration'] as String?,
    nomAuteurDeclaration: j['nom_auteur_declaration'] as String?,
    blocage: j['blocage'] == null
        ? null
        : Blocage.fromJson(j['blocage'] as Map<String, dynamic>),
  );

  /// Numéro d'étape affiché (« 104 »).
  final String id;
  final String libelle;
  final String detail;
  final String corpsEtat;
  final String zone;
  final StatutEtape statut;
  final String equipe;
  final String idResponsable;
  final String nomResponsable;

  /// Quantité d'ouvrage à réaliser et quantité déjà pointée.
  final num metreCible;
  final num metreFait;
  final String uniteMetre;

  /// Points de contrôle de la gamme opératoire, et leur état.
  final List<String> controles;
  final List<bool> controlesFaits;

  /// Vrai si l'étape exige une validation explicite par un tiers.
  final bool controleRequis;

  /// Temps déjà pointé, hors session en cours.
  final int secondesPointees;
  final String? horaire;

  /// Début de la session de pointage active ; `null` si le pointage est arrêté.
  final DateTime? debutPointage;

  /// Auteur de la déclaration de fin : il ne peut pas valider l'étape.
  final String? idAuteurDeclaration;
  final String? nomAuteurDeclaration;
  final Blocage? blocage;

  double get progression =>
      metreCible <= 0 ? 0 : (metreFait / metreCible).clamp(0, 1).toDouble();

  bool get pointageActif => debutPointage != null;

  bool get controlesComplets => controlesFaits.every((fait) => fait);

  /// Une étape ne peut être déclarée terminée que métré atteint et contrôles
  /// de la gamme tous cochés.
  bool get peutEtreTerminee => metreFait >= metreCible && controlesComplets;

  Duration dureePointee(DateTime maintenant) {
    final debut = debutPointage;
    final session = debut == null ? 0 : maintenant.difference(debut).inSeconds;
    return Duration(seconds: secondesPointees + (session < 0 ? 0 : session));
  }

  EtapeTravaux copie({
    StatutEtape? statut,
    String? equipe,
    String? idResponsable,
    String? nomResponsable,
    num? metreFait,
    List<bool>? controlesFaits,
    int? secondesPointees,
    DateTime? debutPointage,
    bool arreterPointage = false,
    String? idAuteurDeclaration,
    String? nomAuteurDeclaration,
    Blocage? blocage,
    bool leverBlocage = false,
  }) => EtapeTravaux(
    id: id,
    libelle: libelle,
    detail: detail,
    corpsEtat: corpsEtat,
    zone: zone,
    statut: statut ?? this.statut,
    equipe: equipe ?? this.equipe,
    idResponsable: idResponsable ?? this.idResponsable,
    nomResponsable: nomResponsable ?? this.nomResponsable,
    metreCible: metreCible,
    metreFait: metreFait ?? this.metreFait,
    uniteMetre: uniteMetre,
    controles: controles,
    controlesFaits: controlesFaits ?? this.controlesFaits,
    controleRequis: controleRequis,
    secondesPointees: secondesPointees ?? this.secondesPointees,
    horaire: horaire,
    debutPointage: arreterPointage
        ? null
        : (debutPointage ?? this.debutPointage),
    idAuteurDeclaration: idAuteurDeclaration ?? this.idAuteurDeclaration,
    nomAuteurDeclaration: nomAuteurDeclaration ?? this.nomAuteurDeclaration,
    blocage: leverBlocage ? null : (blocage ?? this.blocage),
  );

  Map<String, dynamic> toJson() => {
    'id': id,
    'libelle': libelle,
    'detail': detail,
    'corps_etat': corpsEtat,
    'zone': zone,
    'statut': statut.code,
    'equipe': equipe,
    'id_responsable': idResponsable,
    'nom_responsable': nomResponsable,
    'metre_cible': metreCible,
    'metre_fait': metreFait,
    'unite_metre': uniteMetre,
    'controles': controles,
    'controles_faits': controlesFaits,
    'controle_requis': controleRequis,
    'secondes_pointees': secondesPointees,
    'horaire': horaire,
    'debut_pointage': debutPointage?.toIso8601String(),
    'id_auteur_declaration': idAuteurDeclaration,
    'nom_auteur_declaration': nomAuteurDeclaration,
    'blocage': blocage?.toJson(),
  };
}

/// Nature d'un événement du journal d'étape.
enum TypeEvenement {
  demarrage,
  pointage,
  pause,
  reprise,
  blocage,
  leveeBlocage,
  fin,
  validation,
  rejet,
  reaffectation,
}

/// Événement d'exécution d'une étape : journal horodaté, non modifiable.
class EvenementEtape {
  const EvenementEtape({
    required this.uuid,
    required this.idEtape,
    required this.libelleEtape,
    required this.type,
    required this.date,
    required this.nomAuteur,
    this.detail,
  });

  factory EvenementEtape.fromJson(Map<String, dynamic> j) => EvenementEtape(
    uuid: j['uuid'] as String,
    idEtape: j['id_etape'] as String,
    libelleEtape: j['libelle_etape'] as String,
    type: TypeEvenement.values.byName(j['type'] as String),
    date: DateTime.parse(j['date'] as String),
    nomAuteur: j['nom_auteur'] as String,
    detail: j['detail'] as String?,
  );

  final String uuid;
  final String idEtape;
  final String libelleEtape;
  final TypeEvenement type;
  final DateTime date;
  final String nomAuteur;
  final String? detail;

  Map<String, dynamic> toJson() => {
    'uuid': uuid,
    'id_etape': idEtape,
    'libelle_etape': libelleEtape,
    'type': type.name,
    'date': date.toIso8601String(),
    'nom_auteur': nomAuteur,
    'detail': detail,
  };
}

/// Équipe pouvant reprendre une étape, avec sa charge actuelle (0 à 1).
class Equipe {
  const Equipe({
    required this.nom,
    required this.idChef,
    required this.nomChef,
    required this.effectif,
    required this.charge,
  });

  final String nom;
  final String idChef;
  final String nomChef;
  final int effectif;
  final double charge;
}
