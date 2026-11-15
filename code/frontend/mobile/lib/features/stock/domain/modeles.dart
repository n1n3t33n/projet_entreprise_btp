// Modèle du stock tel que le terrain le manipule (CL-4, ET-2). Mêmes notions
// et mêmes codes que le poste de pilotage web : niveaux Vide / Critique / Mini
// / Plein, types de mouvement, statut de validation.

/// Niveau d'un article par rapport à ses seuils. Un stock négatif est classé
/// « vide » et signalé à part (anomalie non bloquante, charte § 10).
enum NiveauStock { vide, critique, mini, plein }

enum SensMouvement { entree, sortie }

/// Type de mouvement, avec le code partagé avec le serveur.
enum TypeMouvement {
  reception('ENT_RECEPTION'),
  sortieLogement('SOR_LOGEMENT'),
  retour('RET_RETOUR'),
  perte('SOR_PERTE'),
  ajustement('AJU_INVENTAIRE');

  const TypeMouvement(this.code);

  final String code;

  static TypeMouvement parCode(String code) =>
      values.firstWhere((t) => t.code == code, orElse: () => reception);
}

/// Statut de validation d'un mouvement (ET-2).
enum StatutMouvement {
  enregistre('ENREGISTRE'),
  aValider('A_VALIDER'),
  valide('VALIDE'),
  rejete('REJETE');

  const StatutMouvement(this.code);

  final String code;

  static StatutMouvement parCode(String code) =>
      values.firstWhere((s) => s.code == code, orElse: () => enregistre);
}

class ArticleStock {
  const ArticleStock({
    required this.code,
    required this.designation,
    required this.famille,
    required this.unite,
    required this.quantite,
    required this.seuilMinimal,
    required this.seuilCritique,
    required this.capacite,
    required this.emplacement,
    required this.codeBarre,
    required this.majLe,
  });

  factory ArticleStock.fromJson(Map<String, dynamic> j) => ArticleStock(
    code: j['code'] as String,
    designation: j['designation'] as String,
    famille: j['famille'] as String,
    unite: j['unite'] as String,
    quantite: j['quantite'] as num,
    seuilMinimal: j['seuil_minimal'] as num,
    seuilCritique: j['seuil_critique'] as num,
    capacite: j['capacite'] as num,
    emplacement: j['emplacement'] as String,
    codeBarre: j['code_barre'] as String,
    majLe: DateTime.parse(j['maj_le'] as String),
  );

  final String code;
  final String designation;
  final String famille;
  final String unite;
  final num quantite;

  /// Seuil d'alerte : en dessous, il faut réapprovisionner.
  final num seuilMinimal;

  /// Seuil critique : en dessous, la rupture est proche.
  final num seuilCritique;
  final num capacite;
  final String emplacement;
  final String codeBarre;
  final DateTime majLe;

  NiveauStock get niveau {
    if (quantite <= 0) return NiveauStock.vide;
    if (quantite < seuilCritique) return NiveauStock.critique;
    return quantite < seuilMinimal ? NiveauStock.mini : NiveauStock.plein;
  }

  bool get estNegatif => quantite < 0;

  bool get sousSeuil => niveau != NiveauStock.plein;

  ArticleStock avecQuantite(num valeur, DateTime date) => ArticleStock(
    code: code,
    designation: designation,
    famille: famille,
    unite: unite,
    quantite: valeur,
    seuilMinimal: seuilMinimal,
    seuilCritique: seuilCritique,
    capacite: capacite,
    emplacement: emplacement,
    codeBarre: codeBarre,
    majLe: date,
  );

  Map<String, dynamic> toJson() => {
    'code': code,
    'designation': designation,
    'famille': famille,
    'unite': unite,
    'quantite': quantite,
    'seuil_minimal': seuilMinimal,
    'seuil_critique': seuilCritique,
    'capacite': capacite,
    'emplacement': emplacement,
    'code_barre': codeBarre,
    'maj_le': majLe.toIso8601String(),
  };
}

/// Mouvement de stock. Journal non modifiable : une correction passe par un
/// nouveau mouvement, jamais par une modification.
class MouvementStock {
  const MouvementStock({
    required this.uuid,
    required this.numero,
    required this.codeArticle,
    required this.designation,
    required this.unite,
    required this.type,
    required this.sens,
    required this.quantite,
    required this.date,
    required this.idAuteur,
    required this.nomAuteur,
    required this.statut,
    this.destination,
    this.reference,
    this.motif,
  });

  factory MouvementStock.fromJson(Map<String, dynamic> j) => MouvementStock(
    uuid: j['uuid'] as String,
    numero: j['numero'] as String,
    codeArticle: j['code_article'] as String,
    designation: j['designation'] as String,
    unite: j['unite'] as String,
    type: TypeMouvement.parCode(j['type'] as String),
    sens: j['sens'] == 'SORTIE' ? SensMouvement.sortie : SensMouvement.entree,
    quantite: j['quantite'] as num,
    date: DateTime.parse(j['date'] as String),
    idAuteur: j['id_auteur'] as String,
    nomAuteur: j['nom_auteur'] as String,
    statut: StatutMouvement.parCode(j['statut'] as String),
    destination: j['destination'] as String?,
    reference: j['reference'] as String?,
    motif: j['motif'] as String?,
  );

  final String uuid;

  /// Numéro de bon lisible (« SR-884 »).
  final String numero;
  final String codeArticle;
  final String designation;
  final String unite;
  final TypeMouvement type;
  final SensMouvement sens;
  final num quantite;
  final DateTime date;

  /// Auteur : sert au contrôle « celui qui saisit ne valide pas ».
  final String idAuteur;
  final String nomAuteur;
  final StatutMouvement statut;
  final String? destination;
  final String? reference;
  final String? motif;

  /// Quantité signée : négative pour une sortie.
  num get quantiteSignee => sens == SensMouvement.sortie ? -quantite : quantite;

  MouvementStock avecStatut(StatutMouvement nouveau) => MouvementStock(
    uuid: uuid,
    numero: numero,
    codeArticle: codeArticle,
    designation: designation,
    unite: unite,
    type: type,
    sens: sens,
    quantite: quantite,
    date: date,
    idAuteur: idAuteur,
    nomAuteur: nomAuteur,
    statut: nouveau,
    destination: destination,
    reference: reference,
    motif: motif,
  );

  Map<String, dynamic> toJson() => {
    'uuid': uuid,
    'numero': numero,
    'code_article': codeArticle,
    'designation': designation,
    'unite': unite,
    'type': type.code,
    'sens': sens == SensMouvement.sortie ? 'SORTIE' : 'ENTREE',
    'quantite': quantite,
    'date': date.toIso8601String(),
    'id_auteur': idAuteur,
    'nom_auteur': nomAuteur,
    'statut': statut.code,
    'destination': destination,
    'reference': reference,
    'motif': motif,
  };
}

/// Ligne d'un inventaire tournant : quantité attendue et quantité comptée.
class LigneInventaire {
  const LigneInventaire({
    required this.codeArticle,
    required this.designation,
    required this.unite,
    required this.emplacement,
    required this.theorique,
    this.compte,
    this.justification,
  });

  factory LigneInventaire.fromJson(Map<String, dynamic> j) => LigneInventaire(
    codeArticle: j['code_article'] as String,
    designation: j['designation'] as String,
    unite: j['unite'] as String,
    emplacement: j['emplacement'] as String,
    theorique: j['theorique'] as num,
    compte: j['compte'] as num?,
    justification: j['justification'] as String?,
  );

  final String codeArticle;
  final String designation;
  final String unite;
  final String emplacement;
  final num theorique;
  final num? compte;
  final String? justification;

  bool get estComptee => compte != null;

  num get ecart => (compte ?? theorique) - theorique;

  LigneInventaire comptee(num valeur, String? motif) => LigneInventaire(
    codeArticle: codeArticle,
    designation: designation,
    unite: unite,
    emplacement: emplacement,
    theorique: theorique,
    compte: valeur,
    justification: motif,
  );

  Map<String, dynamic> toJson() => {
    'code_article': codeArticle,
    'designation': designation,
    'unite': unite,
    'emplacement': emplacement,
    'theorique': theorique,
    'compte': compte,
    'justification': justification,
  };
}

/// Statut d'un inventaire : en cours de comptage, soumis à validation, validé.
enum StatutInventaire { enCours, aValider, valide }

class Inventaire {
  const Inventaire({
    required this.id,
    required this.zone,
    required this.lignes,
    required this.statut,
    this.idCompteur,
  });

  factory Inventaire.fromJson(Map<String, dynamic> j) => Inventaire(
    id: j['id'] as String,
    zone: j['zone'] as String,
    lignes: [
      for (final l in (j['lignes'] as List<dynamic>))
        LigneInventaire.fromJson(l as Map<String, dynamic>),
    ],
    statut: StatutInventaire.values.byName(j['statut'] as String),
    idCompteur: j['id_compteur'] as String?,
  );

  final String id;
  final String zone;
  final List<LigneInventaire> lignes;
  final StatutInventaire statut;

  /// Opérateur qui a compté : il ne peut pas valider ses propres écarts.
  final String? idCompteur;

  int get nombreComptees => lignes.where((l) => l.estComptee).length;

  double get progression => lignes.isEmpty ? 0 : nombreComptees / lignes.length;

  List<LigneInventaire> get ecarts =>
      lignes.where((l) => l.estComptee && l.ecart != 0).toList();

  Inventaire copie({
    List<LigneInventaire>? lignes,
    StatutInventaire? statut,
    String? idCompteur,
  }) => Inventaire(
    id: id,
    zone: zone,
    lignes: lignes ?? this.lignes,
    statut: statut ?? this.statut,
    idCompteur: idCompteur ?? this.idCompteur,
  );

  Map<String, dynamic> toJson() => {
    'id': id,
    'zone': zone,
    'lignes': [for (final l in lignes) l.toJson()],
    'statut': statut.name,
    'id_compteur': idCompteur,
  };
}

/// Quantité lisible : entier sans décimale, sinon une décimale.
String formaterQuantite(num valeur, [String? unite]) {
  final nombre = valeur == valeur.roundToDouble()
      ? valeur.round().toString()
      : valeur.toStringAsFixed(1).replaceAll('.', ',');
  return unite == null ? nombre : '$nombre $unite';
}
