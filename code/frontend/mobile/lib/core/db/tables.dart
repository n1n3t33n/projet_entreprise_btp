import 'package:drift/drift.dart';

/// Tables locales du modèle de synchronisation (CL-6 / MPD-6).
///
/// Au jalon M1, seules les tables du socle sont définies : session, file
/// d'envoi, cache de référence, journal local, lot de synchronisation et
/// résultat d'événement. Les tables purement métier `stock_local` et
/// `etape_locale` (et `curseur_reference`, `anomalie_synchronisation`) sont
/// reportées aux jalons M2/M3 (voir _handoff/decisions.md).
///
/// Les noms de tables et de colonnes suivent le MPD (snake_case) ; les statuts
/// et énumérés circulent en `UPPER_SNAKE`.

/// Session locale : empreinte du PIN, jeton chiffré, dernière connexion en
/// ligne (ancre du verrou 14 jours — AC-1 / ET-4).
@DataClassName('SessionLocaleRow')
class SessionLocale extends Table {
  @override
  String get tableName => 'session_locale';

  TextColumn get idSession => text().named('id_session')();
  TextColumn get identifiant => text()();
  TextColumn get roleCode => text().named('role_code')();
  TextColumn get jetonChiffre => text().named('jeton_chiffre').nullable()();
  TextColumn get pinHashLocal => text().named('pin_hash_local')();
  TextColumn get pinSel => text().named('pin_sel')();
  DateTimeColumn get derniereConnexionEnLigne =>
      dateTime().named('derniere_connexion_en_ligne')();

  @override
  Set<Column<Object>> get primaryKey => {idSession};
}

/// File d'envoi : événements saisis hors-ligne, en attente de transmission
/// idempotente (ET-3). La clé primaire est l'UUID d'événement : rejouer le même
/// événement ne crée pas de doublon.
@DataClassName('FileEnvoiRow')
class FileEnvoi extends Table {
  @override
  String get tableName => 'file_envoi';

  TextColumn get uuidEvenement => text().named('uuid_evenement')();
  TextColumn get typeEvenement => text().named('type_evenement')();
  TextColumn get chargeUtile => text().named('charge_utile')();
  TextColumn get statut => text()();
  IntColumn get nombreTentatives =>
      integer().named('nombre_tentatives').withDefault(const Constant(0))();
  DateTimeColumn get prochaineTentative =>
      dateTime().named('prochaine_tentative').nullable()();
  TextColumn get sessionLocaleId =>
      text().named('session_locale_id_session').nullable()();
  TextColumn get lotSynchronisationId =>
      text().named('lot_synchronisation_id_lot').nullable()();

  @override
  Set<Column<Object>> get primaryKey => {uuidEvenement};
}

/// Cache de référence : données serveur consultables hors-ligne.
@DataClassName('CacheReferenceRow')
class CacheReference extends Table {
  @override
  String get tableName => 'cache_reference';

  TextColumn get typeDonnee => text().named('type_donnee')();
  TextColumn get cle => text()();
  TextColumn get contenu => text()();
  IntColumn get version => integer()();

  @override
  Set<Column<Object>> get primaryKey => {typeDonnee, cle};
}

/// Journal local : trace des actions sur l'appareil.
@DataClassName('JournalLocalRow')
class JournalLocal extends Table {
  @override
  String get tableName => 'journal_local';

  TextColumn get idEntree => text().named('id_entree')();
  TextColumn get evenement => text()();
  DateTimeColumn get horodatage => dateTime()();
  TextColumn get sessionLocaleId =>
      text().named('session_locale_id_session').nullable()();

  @override
  Set<Column<Object>> get primaryKey => {idEntree};
}

/// Lot de synchronisation : compte rendu d'un envoi vers le serveur.
@DataClassName('LotSynchronisationRow')
class LotSynchronisation extends Table {
  @override
  String get tableName => 'lot_synchronisation';

  TextColumn get idLot => text().named('id_lot')();
  DateTimeColumn get dateReception =>
      dateTime().named('date_reception').nullable()();
  IntColumn get nombreEvenements =>
      integer().named('nombre_evenements').withDefault(const Constant(0))();
  IntColumn get nombreAcceptes =>
      integer().named('nombre_acceptes').withDefault(const Constant(0))();
  IntColumn get nombreRejetes =>
      integer().named('nombre_rejetes').withDefault(const Constant(0))();
  IntColumn get dureeMs => integer().named('duree_ms').nullable()();

  @override
  Set<Column<Object>> get primaryKey => {idLot};
}

/// Résultat par événement renvoyé par le serveur dans un lot.
@DataClassName('ResultatEvenementRow')
class ResultatEvenement extends Table {
  @override
  String get tableName => 'resultat_evenement';

  TextColumn get idResultat => text().named('id_resultat')();
  TextColumn get uuidEvenement => text().named('uuid_evenement')();
  TextColumn get statut => text()();
  TextColumn get motifRejet => text().named('motif_rejet').nullable()();
  TextColumn get lotSynchronisationId =>
      text().named('lot_synchronisation_id_lot')();

  @override
  Set<Column<Object>> get primaryKey => {idResultat};
}
