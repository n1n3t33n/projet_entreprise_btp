// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'base_locale.dart';

// ignore_for_file: type=lint
class $SessionLocaleTable extends SessionLocale
    with TableInfo<$SessionLocaleTable, SessionLocaleRow> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $SessionLocaleTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idSessionMeta = const VerificationMeta(
    'idSession',
  );
  @override
  late final GeneratedColumn<String> idSession = GeneratedColumn<String>(
    'id_session',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _identifiantMeta = const VerificationMeta(
    'identifiant',
  );
  @override
  late final GeneratedColumn<String> identifiant = GeneratedColumn<String>(
    'identifiant',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _roleCodeMeta = const VerificationMeta(
    'roleCode',
  );
  @override
  late final GeneratedColumn<String> roleCode = GeneratedColumn<String>(
    'role_code',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _jetonChiffreMeta = const VerificationMeta(
    'jetonChiffre',
  );
  @override
  late final GeneratedColumn<String> jetonChiffre = GeneratedColumn<String>(
    'jeton_chiffre',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _pinHashLocalMeta = const VerificationMeta(
    'pinHashLocal',
  );
  @override
  late final GeneratedColumn<String> pinHashLocal = GeneratedColumn<String>(
    'pin_hash_local',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _pinSelMeta = const VerificationMeta('pinSel');
  @override
  late final GeneratedColumn<String> pinSel = GeneratedColumn<String>(
    'pin_sel',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _derniereConnexionEnLigneMeta =
      const VerificationMeta('derniereConnexionEnLigne');
  @override
  late final GeneratedColumn<DateTime> derniereConnexionEnLigne =
      GeneratedColumn<DateTime>(
        'derniere_connexion_en_ligne',
        aliasedName,
        false,
        type: DriftSqlType.dateTime,
        requiredDuringInsert: true,
      );
  @override
  List<GeneratedColumn> get $columns => [
    idSession,
    identifiant,
    roleCode,
    jetonChiffre,
    pinHashLocal,
    pinSel,
    derniereConnexionEnLigne,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'session_locale';
  @override
  VerificationContext validateIntegrity(
    Insertable<SessionLocaleRow> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id_session')) {
      context.handle(
        _idSessionMeta,
        idSession.isAcceptableOrUnknown(data['id_session']!, _idSessionMeta),
      );
    } else if (isInserting) {
      context.missing(_idSessionMeta);
    }
    if (data.containsKey('identifiant')) {
      context.handle(
        _identifiantMeta,
        identifiant.isAcceptableOrUnknown(
          data['identifiant']!,
          _identifiantMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_identifiantMeta);
    }
    if (data.containsKey('role_code')) {
      context.handle(
        _roleCodeMeta,
        roleCode.isAcceptableOrUnknown(data['role_code']!, _roleCodeMeta),
      );
    } else if (isInserting) {
      context.missing(_roleCodeMeta);
    }
    if (data.containsKey('jeton_chiffre')) {
      context.handle(
        _jetonChiffreMeta,
        jetonChiffre.isAcceptableOrUnknown(
          data['jeton_chiffre']!,
          _jetonChiffreMeta,
        ),
      );
    }
    if (data.containsKey('pin_hash_local')) {
      context.handle(
        _pinHashLocalMeta,
        pinHashLocal.isAcceptableOrUnknown(
          data['pin_hash_local']!,
          _pinHashLocalMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_pinHashLocalMeta);
    }
    if (data.containsKey('pin_sel')) {
      context.handle(
        _pinSelMeta,
        pinSel.isAcceptableOrUnknown(data['pin_sel']!, _pinSelMeta),
      );
    } else if (isInserting) {
      context.missing(_pinSelMeta);
    }
    if (data.containsKey('derniere_connexion_en_ligne')) {
      context.handle(
        _derniereConnexionEnLigneMeta,
        derniereConnexionEnLigne.isAcceptableOrUnknown(
          data['derniere_connexion_en_ligne']!,
          _derniereConnexionEnLigneMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_derniereConnexionEnLigneMeta);
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {idSession};
  @override
  SessionLocaleRow map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return SessionLocaleRow(
      idSession: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}id_session'],
      )!,
      identifiant: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}identifiant'],
      )!,
      roleCode: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}role_code'],
      )!,
      jetonChiffre: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}jeton_chiffre'],
      ),
      pinHashLocal: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}pin_hash_local'],
      )!,
      pinSel: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}pin_sel'],
      )!,
      derniereConnexionEnLigne: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}derniere_connexion_en_ligne'],
      )!,
    );
  }

  @override
  $SessionLocaleTable createAlias(String alias) {
    return $SessionLocaleTable(attachedDatabase, alias);
  }
}

class SessionLocaleRow extends DataClass
    implements Insertable<SessionLocaleRow> {
  final String idSession;
  final String identifiant;
  final String roleCode;
  final String? jetonChiffre;
  final String pinHashLocal;
  final String pinSel;
  final DateTime derniereConnexionEnLigne;
  const SessionLocaleRow({
    required this.idSession,
    required this.identifiant,
    required this.roleCode,
    this.jetonChiffre,
    required this.pinHashLocal,
    required this.pinSel,
    required this.derniereConnexionEnLigne,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id_session'] = Variable<String>(idSession);
    map['identifiant'] = Variable<String>(identifiant);
    map['role_code'] = Variable<String>(roleCode);
    if (!nullToAbsent || jetonChiffre != null) {
      map['jeton_chiffre'] = Variable<String>(jetonChiffre);
    }
    map['pin_hash_local'] = Variable<String>(pinHashLocal);
    map['pin_sel'] = Variable<String>(pinSel);
    map['derniere_connexion_en_ligne'] = Variable<DateTime>(
      derniereConnexionEnLigne,
    );
    return map;
  }

  SessionLocaleCompanion toCompanion(bool nullToAbsent) {
    return SessionLocaleCompanion(
      idSession: Value(idSession),
      identifiant: Value(identifiant),
      roleCode: Value(roleCode),
      jetonChiffre: jetonChiffre == null && nullToAbsent
          ? const Value.absent()
          : Value(jetonChiffre),
      pinHashLocal: Value(pinHashLocal),
      pinSel: Value(pinSel),
      derniereConnexionEnLigne: Value(derniereConnexionEnLigne),
    );
  }

  factory SessionLocaleRow.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return SessionLocaleRow(
      idSession: serializer.fromJson<String>(json['idSession']),
      identifiant: serializer.fromJson<String>(json['identifiant']),
      roleCode: serializer.fromJson<String>(json['roleCode']),
      jetonChiffre: serializer.fromJson<String?>(json['jetonChiffre']),
      pinHashLocal: serializer.fromJson<String>(json['pinHashLocal']),
      pinSel: serializer.fromJson<String>(json['pinSel']),
      derniereConnexionEnLigne: serializer.fromJson<DateTime>(
        json['derniereConnexionEnLigne'],
      ),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'idSession': serializer.toJson<String>(idSession),
      'identifiant': serializer.toJson<String>(identifiant),
      'roleCode': serializer.toJson<String>(roleCode),
      'jetonChiffre': serializer.toJson<String?>(jetonChiffre),
      'pinHashLocal': serializer.toJson<String>(pinHashLocal),
      'pinSel': serializer.toJson<String>(pinSel),
      'derniereConnexionEnLigne': serializer.toJson<DateTime>(
        derniereConnexionEnLigne,
      ),
    };
  }

  SessionLocaleRow copyWith({
    String? idSession,
    String? identifiant,
    String? roleCode,
    Value<String?> jetonChiffre = const Value.absent(),
    String? pinHashLocal,
    String? pinSel,
    DateTime? derniereConnexionEnLigne,
  }) => SessionLocaleRow(
    idSession: idSession ?? this.idSession,
    identifiant: identifiant ?? this.identifiant,
    roleCode: roleCode ?? this.roleCode,
    jetonChiffre: jetonChiffre.present ? jetonChiffre.value : this.jetonChiffre,
    pinHashLocal: pinHashLocal ?? this.pinHashLocal,
    pinSel: pinSel ?? this.pinSel,
    derniereConnexionEnLigne:
        derniereConnexionEnLigne ?? this.derniereConnexionEnLigne,
  );
  SessionLocaleRow copyWithCompanion(SessionLocaleCompanion data) {
    return SessionLocaleRow(
      idSession: data.idSession.present ? data.idSession.value : this.idSession,
      identifiant: data.identifiant.present
          ? data.identifiant.value
          : this.identifiant,
      roleCode: data.roleCode.present ? data.roleCode.value : this.roleCode,
      jetonChiffre: data.jetonChiffre.present
          ? data.jetonChiffre.value
          : this.jetonChiffre,
      pinHashLocal: data.pinHashLocal.present
          ? data.pinHashLocal.value
          : this.pinHashLocal,
      pinSel: data.pinSel.present ? data.pinSel.value : this.pinSel,
      derniereConnexionEnLigne: data.derniereConnexionEnLigne.present
          ? data.derniereConnexionEnLigne.value
          : this.derniereConnexionEnLigne,
    );
  }

  @override
  String toString() {
    return (StringBuffer('SessionLocaleRow(')
          ..write('idSession: $idSession, ')
          ..write('identifiant: $identifiant, ')
          ..write('roleCode: $roleCode, ')
          ..write('jetonChiffre: $jetonChiffre, ')
          ..write('pinHashLocal: $pinHashLocal, ')
          ..write('pinSel: $pinSel, ')
          ..write('derniereConnexionEnLigne: $derniereConnexionEnLigne')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
    idSession,
    identifiant,
    roleCode,
    jetonChiffre,
    pinHashLocal,
    pinSel,
    derniereConnexionEnLigne,
  );
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is SessionLocaleRow &&
          other.idSession == this.idSession &&
          other.identifiant == this.identifiant &&
          other.roleCode == this.roleCode &&
          other.jetonChiffre == this.jetonChiffre &&
          other.pinHashLocal == this.pinHashLocal &&
          other.pinSel == this.pinSel &&
          other.derniereConnexionEnLigne == this.derniereConnexionEnLigne);
}

class SessionLocaleCompanion extends UpdateCompanion<SessionLocaleRow> {
  final Value<String> idSession;
  final Value<String> identifiant;
  final Value<String> roleCode;
  final Value<String?> jetonChiffre;
  final Value<String> pinHashLocal;
  final Value<String> pinSel;
  final Value<DateTime> derniereConnexionEnLigne;
  final Value<int> rowid;
  const SessionLocaleCompanion({
    this.idSession = const Value.absent(),
    this.identifiant = const Value.absent(),
    this.roleCode = const Value.absent(),
    this.jetonChiffre = const Value.absent(),
    this.pinHashLocal = const Value.absent(),
    this.pinSel = const Value.absent(),
    this.derniereConnexionEnLigne = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  SessionLocaleCompanion.insert({
    required String idSession,
    required String identifiant,
    required String roleCode,
    this.jetonChiffre = const Value.absent(),
    required String pinHashLocal,
    required String pinSel,
    required DateTime derniereConnexionEnLigne,
    this.rowid = const Value.absent(),
  }) : idSession = Value(idSession),
       identifiant = Value(identifiant),
       roleCode = Value(roleCode),
       pinHashLocal = Value(pinHashLocal),
       pinSel = Value(pinSel),
       derniereConnexionEnLigne = Value(derniereConnexionEnLigne);
  static Insertable<SessionLocaleRow> custom({
    Expression<String>? idSession,
    Expression<String>? identifiant,
    Expression<String>? roleCode,
    Expression<String>? jetonChiffre,
    Expression<String>? pinHashLocal,
    Expression<String>? pinSel,
    Expression<DateTime>? derniereConnexionEnLigne,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (idSession != null) 'id_session': idSession,
      if (identifiant != null) 'identifiant': identifiant,
      if (roleCode != null) 'role_code': roleCode,
      if (jetonChiffre != null) 'jeton_chiffre': jetonChiffre,
      if (pinHashLocal != null) 'pin_hash_local': pinHashLocal,
      if (pinSel != null) 'pin_sel': pinSel,
      if (derniereConnexionEnLigne != null)
        'derniere_connexion_en_ligne': derniereConnexionEnLigne,
      if (rowid != null) 'rowid': rowid,
    });
  }

  SessionLocaleCompanion copyWith({
    Value<String>? idSession,
    Value<String>? identifiant,
    Value<String>? roleCode,
    Value<String?>? jetonChiffre,
    Value<String>? pinHashLocal,
    Value<String>? pinSel,
    Value<DateTime>? derniereConnexionEnLigne,
    Value<int>? rowid,
  }) {
    return SessionLocaleCompanion(
      idSession: idSession ?? this.idSession,
      identifiant: identifiant ?? this.identifiant,
      roleCode: roleCode ?? this.roleCode,
      jetonChiffre: jetonChiffre ?? this.jetonChiffre,
      pinHashLocal: pinHashLocal ?? this.pinHashLocal,
      pinSel: pinSel ?? this.pinSel,
      derniereConnexionEnLigne:
          derniereConnexionEnLigne ?? this.derniereConnexionEnLigne,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (idSession.present) {
      map['id_session'] = Variable<String>(idSession.value);
    }
    if (identifiant.present) {
      map['identifiant'] = Variable<String>(identifiant.value);
    }
    if (roleCode.present) {
      map['role_code'] = Variable<String>(roleCode.value);
    }
    if (jetonChiffre.present) {
      map['jeton_chiffre'] = Variable<String>(jetonChiffre.value);
    }
    if (pinHashLocal.present) {
      map['pin_hash_local'] = Variable<String>(pinHashLocal.value);
    }
    if (pinSel.present) {
      map['pin_sel'] = Variable<String>(pinSel.value);
    }
    if (derniereConnexionEnLigne.present) {
      map['derniere_connexion_en_ligne'] = Variable<DateTime>(
        derniereConnexionEnLigne.value,
      );
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('SessionLocaleCompanion(')
          ..write('idSession: $idSession, ')
          ..write('identifiant: $identifiant, ')
          ..write('roleCode: $roleCode, ')
          ..write('jetonChiffre: $jetonChiffre, ')
          ..write('pinHashLocal: $pinHashLocal, ')
          ..write('pinSel: $pinSel, ')
          ..write('derniereConnexionEnLigne: $derniereConnexionEnLigne, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $FileEnvoiTable extends FileEnvoi
    with TableInfo<$FileEnvoiTable, FileEnvoiRow> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $FileEnvoiTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _uuidEvenementMeta = const VerificationMeta(
    'uuidEvenement',
  );
  @override
  late final GeneratedColumn<String> uuidEvenement = GeneratedColumn<String>(
    'uuid_evenement',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _typeEvenementMeta = const VerificationMeta(
    'typeEvenement',
  );
  @override
  late final GeneratedColumn<String> typeEvenement = GeneratedColumn<String>(
    'type_evenement',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _chargeUtileMeta = const VerificationMeta(
    'chargeUtile',
  );
  @override
  late final GeneratedColumn<String> chargeUtile = GeneratedColumn<String>(
    'charge_utile',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _statutMeta = const VerificationMeta('statut');
  @override
  late final GeneratedColumn<String> statut = GeneratedColumn<String>(
    'statut',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _nombreTentativesMeta = const VerificationMeta(
    'nombreTentatives',
  );
  @override
  late final GeneratedColumn<int> nombreTentatives = GeneratedColumn<int>(
    'nombre_tentatives',
    aliasedName,
    false,
    type: DriftSqlType.int,
    requiredDuringInsert: false,
    defaultValue: const Constant(0),
  );
  static const VerificationMeta _prochaineTentativeMeta =
      const VerificationMeta('prochaineTentative');
  @override
  late final GeneratedColumn<DateTime> prochaineTentative =
      GeneratedColumn<DateTime>(
        'prochaine_tentative',
        aliasedName,
        true,
        type: DriftSqlType.dateTime,
        requiredDuringInsert: false,
      );
  static const VerificationMeta _sessionLocaleIdMeta = const VerificationMeta(
    'sessionLocaleId',
  );
  @override
  late final GeneratedColumn<String> sessionLocaleId = GeneratedColumn<String>(
    'session_locale_id_session',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _lotSynchronisationIdMeta =
      const VerificationMeta('lotSynchronisationId');
  @override
  late final GeneratedColumn<String> lotSynchronisationId =
      GeneratedColumn<String>(
        'lot_synchronisation_id_lot',
        aliasedName,
        true,
        type: DriftSqlType.string,
        requiredDuringInsert: false,
      );
  @override
  List<GeneratedColumn> get $columns => [
    uuidEvenement,
    typeEvenement,
    chargeUtile,
    statut,
    nombreTentatives,
    prochaineTentative,
    sessionLocaleId,
    lotSynchronisationId,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'file_envoi';
  @override
  VerificationContext validateIntegrity(
    Insertable<FileEnvoiRow> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('uuid_evenement')) {
      context.handle(
        _uuidEvenementMeta,
        uuidEvenement.isAcceptableOrUnknown(
          data['uuid_evenement']!,
          _uuidEvenementMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_uuidEvenementMeta);
    }
    if (data.containsKey('type_evenement')) {
      context.handle(
        _typeEvenementMeta,
        typeEvenement.isAcceptableOrUnknown(
          data['type_evenement']!,
          _typeEvenementMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_typeEvenementMeta);
    }
    if (data.containsKey('charge_utile')) {
      context.handle(
        _chargeUtileMeta,
        chargeUtile.isAcceptableOrUnknown(
          data['charge_utile']!,
          _chargeUtileMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_chargeUtileMeta);
    }
    if (data.containsKey('statut')) {
      context.handle(
        _statutMeta,
        statut.isAcceptableOrUnknown(data['statut']!, _statutMeta),
      );
    } else if (isInserting) {
      context.missing(_statutMeta);
    }
    if (data.containsKey('nombre_tentatives')) {
      context.handle(
        _nombreTentativesMeta,
        nombreTentatives.isAcceptableOrUnknown(
          data['nombre_tentatives']!,
          _nombreTentativesMeta,
        ),
      );
    }
    if (data.containsKey('prochaine_tentative')) {
      context.handle(
        _prochaineTentativeMeta,
        prochaineTentative.isAcceptableOrUnknown(
          data['prochaine_tentative']!,
          _prochaineTentativeMeta,
        ),
      );
    }
    if (data.containsKey('session_locale_id_session')) {
      context.handle(
        _sessionLocaleIdMeta,
        sessionLocaleId.isAcceptableOrUnknown(
          data['session_locale_id_session']!,
          _sessionLocaleIdMeta,
        ),
      );
    }
    if (data.containsKey('lot_synchronisation_id_lot')) {
      context.handle(
        _lotSynchronisationIdMeta,
        lotSynchronisationId.isAcceptableOrUnknown(
          data['lot_synchronisation_id_lot']!,
          _lotSynchronisationIdMeta,
        ),
      );
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {uuidEvenement};
  @override
  FileEnvoiRow map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return FileEnvoiRow(
      uuidEvenement: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}uuid_evenement'],
      )!,
      typeEvenement: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}type_evenement'],
      )!,
      chargeUtile: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}charge_utile'],
      )!,
      statut: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}statut'],
      )!,
      nombreTentatives: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}nombre_tentatives'],
      )!,
      prochaineTentative: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}prochaine_tentative'],
      ),
      sessionLocaleId: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}session_locale_id_session'],
      ),
      lotSynchronisationId: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}lot_synchronisation_id_lot'],
      ),
    );
  }

  @override
  $FileEnvoiTable createAlias(String alias) {
    return $FileEnvoiTable(attachedDatabase, alias);
  }
}

class FileEnvoiRow extends DataClass implements Insertable<FileEnvoiRow> {
  final String uuidEvenement;
  final String typeEvenement;
  final String chargeUtile;
  final String statut;
  final int nombreTentatives;
  final DateTime? prochaineTentative;
  final String? sessionLocaleId;
  final String? lotSynchronisationId;
  const FileEnvoiRow({
    required this.uuidEvenement,
    required this.typeEvenement,
    required this.chargeUtile,
    required this.statut,
    required this.nombreTentatives,
    this.prochaineTentative,
    this.sessionLocaleId,
    this.lotSynchronisationId,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['uuid_evenement'] = Variable<String>(uuidEvenement);
    map['type_evenement'] = Variable<String>(typeEvenement);
    map['charge_utile'] = Variable<String>(chargeUtile);
    map['statut'] = Variable<String>(statut);
    map['nombre_tentatives'] = Variable<int>(nombreTentatives);
    if (!nullToAbsent || prochaineTentative != null) {
      map['prochaine_tentative'] = Variable<DateTime>(prochaineTentative);
    }
    if (!nullToAbsent || sessionLocaleId != null) {
      map['session_locale_id_session'] = Variable<String>(sessionLocaleId);
    }
    if (!nullToAbsent || lotSynchronisationId != null) {
      map['lot_synchronisation_id_lot'] = Variable<String>(
        lotSynchronisationId,
      );
    }
    return map;
  }

  FileEnvoiCompanion toCompanion(bool nullToAbsent) {
    return FileEnvoiCompanion(
      uuidEvenement: Value(uuidEvenement),
      typeEvenement: Value(typeEvenement),
      chargeUtile: Value(chargeUtile),
      statut: Value(statut),
      nombreTentatives: Value(nombreTentatives),
      prochaineTentative: prochaineTentative == null && nullToAbsent
          ? const Value.absent()
          : Value(prochaineTentative),
      sessionLocaleId: sessionLocaleId == null && nullToAbsent
          ? const Value.absent()
          : Value(sessionLocaleId),
      lotSynchronisationId: lotSynchronisationId == null && nullToAbsent
          ? const Value.absent()
          : Value(lotSynchronisationId),
    );
  }

  factory FileEnvoiRow.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return FileEnvoiRow(
      uuidEvenement: serializer.fromJson<String>(json['uuidEvenement']),
      typeEvenement: serializer.fromJson<String>(json['typeEvenement']),
      chargeUtile: serializer.fromJson<String>(json['chargeUtile']),
      statut: serializer.fromJson<String>(json['statut']),
      nombreTentatives: serializer.fromJson<int>(json['nombreTentatives']),
      prochaineTentative: serializer.fromJson<DateTime?>(
        json['prochaineTentative'],
      ),
      sessionLocaleId: serializer.fromJson<String?>(json['sessionLocaleId']),
      lotSynchronisationId: serializer.fromJson<String?>(
        json['lotSynchronisationId'],
      ),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'uuidEvenement': serializer.toJson<String>(uuidEvenement),
      'typeEvenement': serializer.toJson<String>(typeEvenement),
      'chargeUtile': serializer.toJson<String>(chargeUtile),
      'statut': serializer.toJson<String>(statut),
      'nombreTentatives': serializer.toJson<int>(nombreTentatives),
      'prochaineTentative': serializer.toJson<DateTime?>(prochaineTentative),
      'sessionLocaleId': serializer.toJson<String?>(sessionLocaleId),
      'lotSynchronisationId': serializer.toJson<String?>(lotSynchronisationId),
    };
  }

  FileEnvoiRow copyWith({
    String? uuidEvenement,
    String? typeEvenement,
    String? chargeUtile,
    String? statut,
    int? nombreTentatives,
    Value<DateTime?> prochaineTentative = const Value.absent(),
    Value<String?> sessionLocaleId = const Value.absent(),
    Value<String?> lotSynchronisationId = const Value.absent(),
  }) => FileEnvoiRow(
    uuidEvenement: uuidEvenement ?? this.uuidEvenement,
    typeEvenement: typeEvenement ?? this.typeEvenement,
    chargeUtile: chargeUtile ?? this.chargeUtile,
    statut: statut ?? this.statut,
    nombreTentatives: nombreTentatives ?? this.nombreTentatives,
    prochaineTentative: prochaineTentative.present
        ? prochaineTentative.value
        : this.prochaineTentative,
    sessionLocaleId: sessionLocaleId.present
        ? sessionLocaleId.value
        : this.sessionLocaleId,
    lotSynchronisationId: lotSynchronisationId.present
        ? lotSynchronisationId.value
        : this.lotSynchronisationId,
  );
  FileEnvoiRow copyWithCompanion(FileEnvoiCompanion data) {
    return FileEnvoiRow(
      uuidEvenement: data.uuidEvenement.present
          ? data.uuidEvenement.value
          : this.uuidEvenement,
      typeEvenement: data.typeEvenement.present
          ? data.typeEvenement.value
          : this.typeEvenement,
      chargeUtile: data.chargeUtile.present
          ? data.chargeUtile.value
          : this.chargeUtile,
      statut: data.statut.present ? data.statut.value : this.statut,
      nombreTentatives: data.nombreTentatives.present
          ? data.nombreTentatives.value
          : this.nombreTentatives,
      prochaineTentative: data.prochaineTentative.present
          ? data.prochaineTentative.value
          : this.prochaineTentative,
      sessionLocaleId: data.sessionLocaleId.present
          ? data.sessionLocaleId.value
          : this.sessionLocaleId,
      lotSynchronisationId: data.lotSynchronisationId.present
          ? data.lotSynchronisationId.value
          : this.lotSynchronisationId,
    );
  }

  @override
  String toString() {
    return (StringBuffer('FileEnvoiRow(')
          ..write('uuidEvenement: $uuidEvenement, ')
          ..write('typeEvenement: $typeEvenement, ')
          ..write('chargeUtile: $chargeUtile, ')
          ..write('statut: $statut, ')
          ..write('nombreTentatives: $nombreTentatives, ')
          ..write('prochaineTentative: $prochaineTentative, ')
          ..write('sessionLocaleId: $sessionLocaleId, ')
          ..write('lotSynchronisationId: $lotSynchronisationId')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
    uuidEvenement,
    typeEvenement,
    chargeUtile,
    statut,
    nombreTentatives,
    prochaineTentative,
    sessionLocaleId,
    lotSynchronisationId,
  );
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is FileEnvoiRow &&
          other.uuidEvenement == this.uuidEvenement &&
          other.typeEvenement == this.typeEvenement &&
          other.chargeUtile == this.chargeUtile &&
          other.statut == this.statut &&
          other.nombreTentatives == this.nombreTentatives &&
          other.prochaineTentative == this.prochaineTentative &&
          other.sessionLocaleId == this.sessionLocaleId &&
          other.lotSynchronisationId == this.lotSynchronisationId);
}

class FileEnvoiCompanion extends UpdateCompanion<FileEnvoiRow> {
  final Value<String> uuidEvenement;
  final Value<String> typeEvenement;
  final Value<String> chargeUtile;
  final Value<String> statut;
  final Value<int> nombreTentatives;
  final Value<DateTime?> prochaineTentative;
  final Value<String?> sessionLocaleId;
  final Value<String?> lotSynchronisationId;
  final Value<int> rowid;
  const FileEnvoiCompanion({
    this.uuidEvenement = const Value.absent(),
    this.typeEvenement = const Value.absent(),
    this.chargeUtile = const Value.absent(),
    this.statut = const Value.absent(),
    this.nombreTentatives = const Value.absent(),
    this.prochaineTentative = const Value.absent(),
    this.sessionLocaleId = const Value.absent(),
    this.lotSynchronisationId = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  FileEnvoiCompanion.insert({
    required String uuidEvenement,
    required String typeEvenement,
    required String chargeUtile,
    required String statut,
    this.nombreTentatives = const Value.absent(),
    this.prochaineTentative = const Value.absent(),
    this.sessionLocaleId = const Value.absent(),
    this.lotSynchronisationId = const Value.absent(),
    this.rowid = const Value.absent(),
  }) : uuidEvenement = Value(uuidEvenement),
       typeEvenement = Value(typeEvenement),
       chargeUtile = Value(chargeUtile),
       statut = Value(statut);
  static Insertable<FileEnvoiRow> custom({
    Expression<String>? uuidEvenement,
    Expression<String>? typeEvenement,
    Expression<String>? chargeUtile,
    Expression<String>? statut,
    Expression<int>? nombreTentatives,
    Expression<DateTime>? prochaineTentative,
    Expression<String>? sessionLocaleId,
    Expression<String>? lotSynchronisationId,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (uuidEvenement != null) 'uuid_evenement': uuidEvenement,
      if (typeEvenement != null) 'type_evenement': typeEvenement,
      if (chargeUtile != null) 'charge_utile': chargeUtile,
      if (statut != null) 'statut': statut,
      if (nombreTentatives != null) 'nombre_tentatives': nombreTentatives,
      if (prochaineTentative != null) 'prochaine_tentative': prochaineTentative,
      if (sessionLocaleId != null) 'session_locale_id_session': sessionLocaleId,
      if (lotSynchronisationId != null)
        'lot_synchronisation_id_lot': lotSynchronisationId,
      if (rowid != null) 'rowid': rowid,
    });
  }

  FileEnvoiCompanion copyWith({
    Value<String>? uuidEvenement,
    Value<String>? typeEvenement,
    Value<String>? chargeUtile,
    Value<String>? statut,
    Value<int>? nombreTentatives,
    Value<DateTime?>? prochaineTentative,
    Value<String?>? sessionLocaleId,
    Value<String?>? lotSynchronisationId,
    Value<int>? rowid,
  }) {
    return FileEnvoiCompanion(
      uuidEvenement: uuidEvenement ?? this.uuidEvenement,
      typeEvenement: typeEvenement ?? this.typeEvenement,
      chargeUtile: chargeUtile ?? this.chargeUtile,
      statut: statut ?? this.statut,
      nombreTentatives: nombreTentatives ?? this.nombreTentatives,
      prochaineTentative: prochaineTentative ?? this.prochaineTentative,
      sessionLocaleId: sessionLocaleId ?? this.sessionLocaleId,
      lotSynchronisationId: lotSynchronisationId ?? this.lotSynchronisationId,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (uuidEvenement.present) {
      map['uuid_evenement'] = Variable<String>(uuidEvenement.value);
    }
    if (typeEvenement.present) {
      map['type_evenement'] = Variable<String>(typeEvenement.value);
    }
    if (chargeUtile.present) {
      map['charge_utile'] = Variable<String>(chargeUtile.value);
    }
    if (statut.present) {
      map['statut'] = Variable<String>(statut.value);
    }
    if (nombreTentatives.present) {
      map['nombre_tentatives'] = Variable<int>(nombreTentatives.value);
    }
    if (prochaineTentative.present) {
      map['prochaine_tentative'] = Variable<DateTime>(prochaineTentative.value);
    }
    if (sessionLocaleId.present) {
      map['session_locale_id_session'] = Variable<String>(
        sessionLocaleId.value,
      );
    }
    if (lotSynchronisationId.present) {
      map['lot_synchronisation_id_lot'] = Variable<String>(
        lotSynchronisationId.value,
      );
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('FileEnvoiCompanion(')
          ..write('uuidEvenement: $uuidEvenement, ')
          ..write('typeEvenement: $typeEvenement, ')
          ..write('chargeUtile: $chargeUtile, ')
          ..write('statut: $statut, ')
          ..write('nombreTentatives: $nombreTentatives, ')
          ..write('prochaineTentative: $prochaineTentative, ')
          ..write('sessionLocaleId: $sessionLocaleId, ')
          ..write('lotSynchronisationId: $lotSynchronisationId, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $CacheReferenceTable extends CacheReference
    with TableInfo<$CacheReferenceTable, CacheReferenceRow> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $CacheReferenceTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _typeDonneeMeta = const VerificationMeta(
    'typeDonnee',
  );
  @override
  late final GeneratedColumn<String> typeDonnee = GeneratedColumn<String>(
    'type_donnee',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _cleMeta = const VerificationMeta('cle');
  @override
  late final GeneratedColumn<String> cle = GeneratedColumn<String>(
    'cle',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _contenuMeta = const VerificationMeta(
    'contenu',
  );
  @override
  late final GeneratedColumn<String> contenu = GeneratedColumn<String>(
    'contenu',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _versionMeta = const VerificationMeta(
    'version',
  );
  @override
  late final GeneratedColumn<int> version = GeneratedColumn<int>(
    'version',
    aliasedName,
    false,
    type: DriftSqlType.int,
    requiredDuringInsert: true,
  );
  @override
  List<GeneratedColumn> get $columns => [typeDonnee, cle, contenu, version];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'cache_reference';
  @override
  VerificationContext validateIntegrity(
    Insertable<CacheReferenceRow> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('type_donnee')) {
      context.handle(
        _typeDonneeMeta,
        typeDonnee.isAcceptableOrUnknown(data['type_donnee']!, _typeDonneeMeta),
      );
    } else if (isInserting) {
      context.missing(_typeDonneeMeta);
    }
    if (data.containsKey('cle')) {
      context.handle(
        _cleMeta,
        cle.isAcceptableOrUnknown(data['cle']!, _cleMeta),
      );
    } else if (isInserting) {
      context.missing(_cleMeta);
    }
    if (data.containsKey('contenu')) {
      context.handle(
        _contenuMeta,
        contenu.isAcceptableOrUnknown(data['contenu']!, _contenuMeta),
      );
    } else if (isInserting) {
      context.missing(_contenuMeta);
    }
    if (data.containsKey('version')) {
      context.handle(
        _versionMeta,
        version.isAcceptableOrUnknown(data['version']!, _versionMeta),
      );
    } else if (isInserting) {
      context.missing(_versionMeta);
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {typeDonnee, cle};
  @override
  CacheReferenceRow map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return CacheReferenceRow(
      typeDonnee: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}type_donnee'],
      )!,
      cle: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}cle'],
      )!,
      contenu: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}contenu'],
      )!,
      version: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}version'],
      )!,
    );
  }

  @override
  $CacheReferenceTable createAlias(String alias) {
    return $CacheReferenceTable(attachedDatabase, alias);
  }
}

class CacheReferenceRow extends DataClass
    implements Insertable<CacheReferenceRow> {
  final String typeDonnee;
  final String cle;
  final String contenu;
  final int version;
  const CacheReferenceRow({
    required this.typeDonnee,
    required this.cle,
    required this.contenu,
    required this.version,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['type_donnee'] = Variable<String>(typeDonnee);
    map['cle'] = Variable<String>(cle);
    map['contenu'] = Variable<String>(contenu);
    map['version'] = Variable<int>(version);
    return map;
  }

  CacheReferenceCompanion toCompanion(bool nullToAbsent) {
    return CacheReferenceCompanion(
      typeDonnee: Value(typeDonnee),
      cle: Value(cle),
      contenu: Value(contenu),
      version: Value(version),
    );
  }

  factory CacheReferenceRow.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return CacheReferenceRow(
      typeDonnee: serializer.fromJson<String>(json['typeDonnee']),
      cle: serializer.fromJson<String>(json['cle']),
      contenu: serializer.fromJson<String>(json['contenu']),
      version: serializer.fromJson<int>(json['version']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'typeDonnee': serializer.toJson<String>(typeDonnee),
      'cle': serializer.toJson<String>(cle),
      'contenu': serializer.toJson<String>(contenu),
      'version': serializer.toJson<int>(version),
    };
  }

  CacheReferenceRow copyWith({
    String? typeDonnee,
    String? cle,
    String? contenu,
    int? version,
  }) => CacheReferenceRow(
    typeDonnee: typeDonnee ?? this.typeDonnee,
    cle: cle ?? this.cle,
    contenu: contenu ?? this.contenu,
    version: version ?? this.version,
  );
  CacheReferenceRow copyWithCompanion(CacheReferenceCompanion data) {
    return CacheReferenceRow(
      typeDonnee: data.typeDonnee.present
          ? data.typeDonnee.value
          : this.typeDonnee,
      cle: data.cle.present ? data.cle.value : this.cle,
      contenu: data.contenu.present ? data.contenu.value : this.contenu,
      version: data.version.present ? data.version.value : this.version,
    );
  }

  @override
  String toString() {
    return (StringBuffer('CacheReferenceRow(')
          ..write('typeDonnee: $typeDonnee, ')
          ..write('cle: $cle, ')
          ..write('contenu: $contenu, ')
          ..write('version: $version')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(typeDonnee, cle, contenu, version);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is CacheReferenceRow &&
          other.typeDonnee == this.typeDonnee &&
          other.cle == this.cle &&
          other.contenu == this.contenu &&
          other.version == this.version);
}

class CacheReferenceCompanion extends UpdateCompanion<CacheReferenceRow> {
  final Value<String> typeDonnee;
  final Value<String> cle;
  final Value<String> contenu;
  final Value<int> version;
  final Value<int> rowid;
  const CacheReferenceCompanion({
    this.typeDonnee = const Value.absent(),
    this.cle = const Value.absent(),
    this.contenu = const Value.absent(),
    this.version = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  CacheReferenceCompanion.insert({
    required String typeDonnee,
    required String cle,
    required String contenu,
    required int version,
    this.rowid = const Value.absent(),
  }) : typeDonnee = Value(typeDonnee),
       cle = Value(cle),
       contenu = Value(contenu),
       version = Value(version);
  static Insertable<CacheReferenceRow> custom({
    Expression<String>? typeDonnee,
    Expression<String>? cle,
    Expression<String>? contenu,
    Expression<int>? version,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (typeDonnee != null) 'type_donnee': typeDonnee,
      if (cle != null) 'cle': cle,
      if (contenu != null) 'contenu': contenu,
      if (version != null) 'version': version,
      if (rowid != null) 'rowid': rowid,
    });
  }

  CacheReferenceCompanion copyWith({
    Value<String>? typeDonnee,
    Value<String>? cle,
    Value<String>? contenu,
    Value<int>? version,
    Value<int>? rowid,
  }) {
    return CacheReferenceCompanion(
      typeDonnee: typeDonnee ?? this.typeDonnee,
      cle: cle ?? this.cle,
      contenu: contenu ?? this.contenu,
      version: version ?? this.version,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (typeDonnee.present) {
      map['type_donnee'] = Variable<String>(typeDonnee.value);
    }
    if (cle.present) {
      map['cle'] = Variable<String>(cle.value);
    }
    if (contenu.present) {
      map['contenu'] = Variable<String>(contenu.value);
    }
    if (version.present) {
      map['version'] = Variable<int>(version.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('CacheReferenceCompanion(')
          ..write('typeDonnee: $typeDonnee, ')
          ..write('cle: $cle, ')
          ..write('contenu: $contenu, ')
          ..write('version: $version, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $JournalLocalTable extends JournalLocal
    with TableInfo<$JournalLocalTable, JournalLocalRow> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $JournalLocalTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idEntreeMeta = const VerificationMeta(
    'idEntree',
  );
  @override
  late final GeneratedColumn<String> idEntree = GeneratedColumn<String>(
    'id_entree',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _evenementMeta = const VerificationMeta(
    'evenement',
  );
  @override
  late final GeneratedColumn<String> evenement = GeneratedColumn<String>(
    'evenement',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _horodatageMeta = const VerificationMeta(
    'horodatage',
  );
  @override
  late final GeneratedColumn<DateTime> horodatage = GeneratedColumn<DateTime>(
    'horodatage',
    aliasedName,
    false,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _sessionLocaleIdMeta = const VerificationMeta(
    'sessionLocaleId',
  );
  @override
  late final GeneratedColumn<String> sessionLocaleId = GeneratedColumn<String>(
    'session_locale_id_session',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  @override
  List<GeneratedColumn> get $columns => [
    idEntree,
    evenement,
    horodatage,
    sessionLocaleId,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'journal_local';
  @override
  VerificationContext validateIntegrity(
    Insertable<JournalLocalRow> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id_entree')) {
      context.handle(
        _idEntreeMeta,
        idEntree.isAcceptableOrUnknown(data['id_entree']!, _idEntreeMeta),
      );
    } else if (isInserting) {
      context.missing(_idEntreeMeta);
    }
    if (data.containsKey('evenement')) {
      context.handle(
        _evenementMeta,
        evenement.isAcceptableOrUnknown(data['evenement']!, _evenementMeta),
      );
    } else if (isInserting) {
      context.missing(_evenementMeta);
    }
    if (data.containsKey('horodatage')) {
      context.handle(
        _horodatageMeta,
        horodatage.isAcceptableOrUnknown(data['horodatage']!, _horodatageMeta),
      );
    } else if (isInserting) {
      context.missing(_horodatageMeta);
    }
    if (data.containsKey('session_locale_id_session')) {
      context.handle(
        _sessionLocaleIdMeta,
        sessionLocaleId.isAcceptableOrUnknown(
          data['session_locale_id_session']!,
          _sessionLocaleIdMeta,
        ),
      );
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {idEntree};
  @override
  JournalLocalRow map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return JournalLocalRow(
      idEntree: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}id_entree'],
      )!,
      evenement: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}evenement'],
      )!,
      horodatage: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}horodatage'],
      )!,
      sessionLocaleId: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}session_locale_id_session'],
      ),
    );
  }

  @override
  $JournalLocalTable createAlias(String alias) {
    return $JournalLocalTable(attachedDatabase, alias);
  }
}

class JournalLocalRow extends DataClass implements Insertable<JournalLocalRow> {
  final String idEntree;
  final String evenement;
  final DateTime horodatage;
  final String? sessionLocaleId;
  const JournalLocalRow({
    required this.idEntree,
    required this.evenement,
    required this.horodatage,
    this.sessionLocaleId,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id_entree'] = Variable<String>(idEntree);
    map['evenement'] = Variable<String>(evenement);
    map['horodatage'] = Variable<DateTime>(horodatage);
    if (!nullToAbsent || sessionLocaleId != null) {
      map['session_locale_id_session'] = Variable<String>(sessionLocaleId);
    }
    return map;
  }

  JournalLocalCompanion toCompanion(bool nullToAbsent) {
    return JournalLocalCompanion(
      idEntree: Value(idEntree),
      evenement: Value(evenement),
      horodatage: Value(horodatage),
      sessionLocaleId: sessionLocaleId == null && nullToAbsent
          ? const Value.absent()
          : Value(sessionLocaleId),
    );
  }

  factory JournalLocalRow.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return JournalLocalRow(
      idEntree: serializer.fromJson<String>(json['idEntree']),
      evenement: serializer.fromJson<String>(json['evenement']),
      horodatage: serializer.fromJson<DateTime>(json['horodatage']),
      sessionLocaleId: serializer.fromJson<String?>(json['sessionLocaleId']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'idEntree': serializer.toJson<String>(idEntree),
      'evenement': serializer.toJson<String>(evenement),
      'horodatage': serializer.toJson<DateTime>(horodatage),
      'sessionLocaleId': serializer.toJson<String?>(sessionLocaleId),
    };
  }

  JournalLocalRow copyWith({
    String? idEntree,
    String? evenement,
    DateTime? horodatage,
    Value<String?> sessionLocaleId = const Value.absent(),
  }) => JournalLocalRow(
    idEntree: idEntree ?? this.idEntree,
    evenement: evenement ?? this.evenement,
    horodatage: horodatage ?? this.horodatage,
    sessionLocaleId: sessionLocaleId.present
        ? sessionLocaleId.value
        : this.sessionLocaleId,
  );
  JournalLocalRow copyWithCompanion(JournalLocalCompanion data) {
    return JournalLocalRow(
      idEntree: data.idEntree.present ? data.idEntree.value : this.idEntree,
      evenement: data.evenement.present ? data.evenement.value : this.evenement,
      horodatage: data.horodatage.present
          ? data.horodatage.value
          : this.horodatage,
      sessionLocaleId: data.sessionLocaleId.present
          ? data.sessionLocaleId.value
          : this.sessionLocaleId,
    );
  }

  @override
  String toString() {
    return (StringBuffer('JournalLocalRow(')
          ..write('idEntree: $idEntree, ')
          ..write('evenement: $evenement, ')
          ..write('horodatage: $horodatage, ')
          ..write('sessionLocaleId: $sessionLocaleId')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode =>
      Object.hash(idEntree, evenement, horodatage, sessionLocaleId);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is JournalLocalRow &&
          other.idEntree == this.idEntree &&
          other.evenement == this.evenement &&
          other.horodatage == this.horodatage &&
          other.sessionLocaleId == this.sessionLocaleId);
}

class JournalLocalCompanion extends UpdateCompanion<JournalLocalRow> {
  final Value<String> idEntree;
  final Value<String> evenement;
  final Value<DateTime> horodatage;
  final Value<String?> sessionLocaleId;
  final Value<int> rowid;
  const JournalLocalCompanion({
    this.idEntree = const Value.absent(),
    this.evenement = const Value.absent(),
    this.horodatage = const Value.absent(),
    this.sessionLocaleId = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  JournalLocalCompanion.insert({
    required String idEntree,
    required String evenement,
    required DateTime horodatage,
    this.sessionLocaleId = const Value.absent(),
    this.rowid = const Value.absent(),
  }) : idEntree = Value(idEntree),
       evenement = Value(evenement),
       horodatage = Value(horodatage);
  static Insertable<JournalLocalRow> custom({
    Expression<String>? idEntree,
    Expression<String>? evenement,
    Expression<DateTime>? horodatage,
    Expression<String>? sessionLocaleId,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (idEntree != null) 'id_entree': idEntree,
      if (evenement != null) 'evenement': evenement,
      if (horodatage != null) 'horodatage': horodatage,
      if (sessionLocaleId != null) 'session_locale_id_session': sessionLocaleId,
      if (rowid != null) 'rowid': rowid,
    });
  }

  JournalLocalCompanion copyWith({
    Value<String>? idEntree,
    Value<String>? evenement,
    Value<DateTime>? horodatage,
    Value<String?>? sessionLocaleId,
    Value<int>? rowid,
  }) {
    return JournalLocalCompanion(
      idEntree: idEntree ?? this.idEntree,
      evenement: evenement ?? this.evenement,
      horodatage: horodatage ?? this.horodatage,
      sessionLocaleId: sessionLocaleId ?? this.sessionLocaleId,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (idEntree.present) {
      map['id_entree'] = Variable<String>(idEntree.value);
    }
    if (evenement.present) {
      map['evenement'] = Variable<String>(evenement.value);
    }
    if (horodatage.present) {
      map['horodatage'] = Variable<DateTime>(horodatage.value);
    }
    if (sessionLocaleId.present) {
      map['session_locale_id_session'] = Variable<String>(
        sessionLocaleId.value,
      );
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('JournalLocalCompanion(')
          ..write('idEntree: $idEntree, ')
          ..write('evenement: $evenement, ')
          ..write('horodatage: $horodatage, ')
          ..write('sessionLocaleId: $sessionLocaleId, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $LotSynchronisationTable extends LotSynchronisation
    with TableInfo<$LotSynchronisationTable, LotSynchronisationRow> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $LotSynchronisationTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idLotMeta = const VerificationMeta('idLot');
  @override
  late final GeneratedColumn<String> idLot = GeneratedColumn<String>(
    'id_lot',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _dateReceptionMeta = const VerificationMeta(
    'dateReception',
  );
  @override
  late final GeneratedColumn<DateTime> dateReception =
      GeneratedColumn<DateTime>(
        'date_reception',
        aliasedName,
        true,
        type: DriftSqlType.dateTime,
        requiredDuringInsert: false,
      );
  static const VerificationMeta _nombreEvenementsMeta = const VerificationMeta(
    'nombreEvenements',
  );
  @override
  late final GeneratedColumn<int> nombreEvenements = GeneratedColumn<int>(
    'nombre_evenements',
    aliasedName,
    false,
    type: DriftSqlType.int,
    requiredDuringInsert: false,
    defaultValue: const Constant(0),
  );
  static const VerificationMeta _nombreAcceptesMeta = const VerificationMeta(
    'nombreAcceptes',
  );
  @override
  late final GeneratedColumn<int> nombreAcceptes = GeneratedColumn<int>(
    'nombre_acceptes',
    aliasedName,
    false,
    type: DriftSqlType.int,
    requiredDuringInsert: false,
    defaultValue: const Constant(0),
  );
  static const VerificationMeta _nombreRejetesMeta = const VerificationMeta(
    'nombreRejetes',
  );
  @override
  late final GeneratedColumn<int> nombreRejetes = GeneratedColumn<int>(
    'nombre_rejetes',
    aliasedName,
    false,
    type: DriftSqlType.int,
    requiredDuringInsert: false,
    defaultValue: const Constant(0),
  );
  static const VerificationMeta _dureeMsMeta = const VerificationMeta(
    'dureeMs',
  );
  @override
  late final GeneratedColumn<int> dureeMs = GeneratedColumn<int>(
    'duree_ms',
    aliasedName,
    true,
    type: DriftSqlType.int,
    requiredDuringInsert: false,
  );
  @override
  List<GeneratedColumn> get $columns => [
    idLot,
    dateReception,
    nombreEvenements,
    nombreAcceptes,
    nombreRejetes,
    dureeMs,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'lot_synchronisation';
  @override
  VerificationContext validateIntegrity(
    Insertable<LotSynchronisationRow> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id_lot')) {
      context.handle(
        _idLotMeta,
        idLot.isAcceptableOrUnknown(data['id_lot']!, _idLotMeta),
      );
    } else if (isInserting) {
      context.missing(_idLotMeta);
    }
    if (data.containsKey('date_reception')) {
      context.handle(
        _dateReceptionMeta,
        dateReception.isAcceptableOrUnknown(
          data['date_reception']!,
          _dateReceptionMeta,
        ),
      );
    }
    if (data.containsKey('nombre_evenements')) {
      context.handle(
        _nombreEvenementsMeta,
        nombreEvenements.isAcceptableOrUnknown(
          data['nombre_evenements']!,
          _nombreEvenementsMeta,
        ),
      );
    }
    if (data.containsKey('nombre_acceptes')) {
      context.handle(
        _nombreAcceptesMeta,
        nombreAcceptes.isAcceptableOrUnknown(
          data['nombre_acceptes']!,
          _nombreAcceptesMeta,
        ),
      );
    }
    if (data.containsKey('nombre_rejetes')) {
      context.handle(
        _nombreRejetesMeta,
        nombreRejetes.isAcceptableOrUnknown(
          data['nombre_rejetes']!,
          _nombreRejetesMeta,
        ),
      );
    }
    if (data.containsKey('duree_ms')) {
      context.handle(
        _dureeMsMeta,
        dureeMs.isAcceptableOrUnknown(data['duree_ms']!, _dureeMsMeta),
      );
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {idLot};
  @override
  LotSynchronisationRow map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return LotSynchronisationRow(
      idLot: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}id_lot'],
      )!,
      dateReception: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}date_reception'],
      ),
      nombreEvenements: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}nombre_evenements'],
      )!,
      nombreAcceptes: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}nombre_acceptes'],
      )!,
      nombreRejetes: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}nombre_rejetes'],
      )!,
      dureeMs: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}duree_ms'],
      ),
    );
  }

  @override
  $LotSynchronisationTable createAlias(String alias) {
    return $LotSynchronisationTable(attachedDatabase, alias);
  }
}

class LotSynchronisationRow extends DataClass
    implements Insertable<LotSynchronisationRow> {
  final String idLot;
  final DateTime? dateReception;
  final int nombreEvenements;
  final int nombreAcceptes;
  final int nombreRejetes;
  final int? dureeMs;
  const LotSynchronisationRow({
    required this.idLot,
    this.dateReception,
    required this.nombreEvenements,
    required this.nombreAcceptes,
    required this.nombreRejetes,
    this.dureeMs,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id_lot'] = Variable<String>(idLot);
    if (!nullToAbsent || dateReception != null) {
      map['date_reception'] = Variable<DateTime>(dateReception);
    }
    map['nombre_evenements'] = Variable<int>(nombreEvenements);
    map['nombre_acceptes'] = Variable<int>(nombreAcceptes);
    map['nombre_rejetes'] = Variable<int>(nombreRejetes);
    if (!nullToAbsent || dureeMs != null) {
      map['duree_ms'] = Variable<int>(dureeMs);
    }
    return map;
  }

  LotSynchronisationCompanion toCompanion(bool nullToAbsent) {
    return LotSynchronisationCompanion(
      idLot: Value(idLot),
      dateReception: dateReception == null && nullToAbsent
          ? const Value.absent()
          : Value(dateReception),
      nombreEvenements: Value(nombreEvenements),
      nombreAcceptes: Value(nombreAcceptes),
      nombreRejetes: Value(nombreRejetes),
      dureeMs: dureeMs == null && nullToAbsent
          ? const Value.absent()
          : Value(dureeMs),
    );
  }

  factory LotSynchronisationRow.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return LotSynchronisationRow(
      idLot: serializer.fromJson<String>(json['idLot']),
      dateReception: serializer.fromJson<DateTime?>(json['dateReception']),
      nombreEvenements: serializer.fromJson<int>(json['nombreEvenements']),
      nombreAcceptes: serializer.fromJson<int>(json['nombreAcceptes']),
      nombreRejetes: serializer.fromJson<int>(json['nombreRejetes']),
      dureeMs: serializer.fromJson<int?>(json['dureeMs']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'idLot': serializer.toJson<String>(idLot),
      'dateReception': serializer.toJson<DateTime?>(dateReception),
      'nombreEvenements': serializer.toJson<int>(nombreEvenements),
      'nombreAcceptes': serializer.toJson<int>(nombreAcceptes),
      'nombreRejetes': serializer.toJson<int>(nombreRejetes),
      'dureeMs': serializer.toJson<int?>(dureeMs),
    };
  }

  LotSynchronisationRow copyWith({
    String? idLot,
    Value<DateTime?> dateReception = const Value.absent(),
    int? nombreEvenements,
    int? nombreAcceptes,
    int? nombreRejetes,
    Value<int?> dureeMs = const Value.absent(),
  }) => LotSynchronisationRow(
    idLot: idLot ?? this.idLot,
    dateReception: dateReception.present
        ? dateReception.value
        : this.dateReception,
    nombreEvenements: nombreEvenements ?? this.nombreEvenements,
    nombreAcceptes: nombreAcceptes ?? this.nombreAcceptes,
    nombreRejetes: nombreRejetes ?? this.nombreRejetes,
    dureeMs: dureeMs.present ? dureeMs.value : this.dureeMs,
  );
  LotSynchronisationRow copyWithCompanion(LotSynchronisationCompanion data) {
    return LotSynchronisationRow(
      idLot: data.idLot.present ? data.idLot.value : this.idLot,
      dateReception: data.dateReception.present
          ? data.dateReception.value
          : this.dateReception,
      nombreEvenements: data.nombreEvenements.present
          ? data.nombreEvenements.value
          : this.nombreEvenements,
      nombreAcceptes: data.nombreAcceptes.present
          ? data.nombreAcceptes.value
          : this.nombreAcceptes,
      nombreRejetes: data.nombreRejetes.present
          ? data.nombreRejetes.value
          : this.nombreRejetes,
      dureeMs: data.dureeMs.present ? data.dureeMs.value : this.dureeMs,
    );
  }

  @override
  String toString() {
    return (StringBuffer('LotSynchronisationRow(')
          ..write('idLot: $idLot, ')
          ..write('dateReception: $dateReception, ')
          ..write('nombreEvenements: $nombreEvenements, ')
          ..write('nombreAcceptes: $nombreAcceptes, ')
          ..write('nombreRejetes: $nombreRejetes, ')
          ..write('dureeMs: $dureeMs')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
    idLot,
    dateReception,
    nombreEvenements,
    nombreAcceptes,
    nombreRejetes,
    dureeMs,
  );
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is LotSynchronisationRow &&
          other.idLot == this.idLot &&
          other.dateReception == this.dateReception &&
          other.nombreEvenements == this.nombreEvenements &&
          other.nombreAcceptes == this.nombreAcceptes &&
          other.nombreRejetes == this.nombreRejetes &&
          other.dureeMs == this.dureeMs);
}

class LotSynchronisationCompanion
    extends UpdateCompanion<LotSynchronisationRow> {
  final Value<String> idLot;
  final Value<DateTime?> dateReception;
  final Value<int> nombreEvenements;
  final Value<int> nombreAcceptes;
  final Value<int> nombreRejetes;
  final Value<int?> dureeMs;
  final Value<int> rowid;
  const LotSynchronisationCompanion({
    this.idLot = const Value.absent(),
    this.dateReception = const Value.absent(),
    this.nombreEvenements = const Value.absent(),
    this.nombreAcceptes = const Value.absent(),
    this.nombreRejetes = const Value.absent(),
    this.dureeMs = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  LotSynchronisationCompanion.insert({
    required String idLot,
    this.dateReception = const Value.absent(),
    this.nombreEvenements = const Value.absent(),
    this.nombreAcceptes = const Value.absent(),
    this.nombreRejetes = const Value.absent(),
    this.dureeMs = const Value.absent(),
    this.rowid = const Value.absent(),
  }) : idLot = Value(idLot);
  static Insertable<LotSynchronisationRow> custom({
    Expression<String>? idLot,
    Expression<DateTime>? dateReception,
    Expression<int>? nombreEvenements,
    Expression<int>? nombreAcceptes,
    Expression<int>? nombreRejetes,
    Expression<int>? dureeMs,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (idLot != null) 'id_lot': idLot,
      if (dateReception != null) 'date_reception': dateReception,
      if (nombreEvenements != null) 'nombre_evenements': nombreEvenements,
      if (nombreAcceptes != null) 'nombre_acceptes': nombreAcceptes,
      if (nombreRejetes != null) 'nombre_rejetes': nombreRejetes,
      if (dureeMs != null) 'duree_ms': dureeMs,
      if (rowid != null) 'rowid': rowid,
    });
  }

  LotSynchronisationCompanion copyWith({
    Value<String>? idLot,
    Value<DateTime?>? dateReception,
    Value<int>? nombreEvenements,
    Value<int>? nombreAcceptes,
    Value<int>? nombreRejetes,
    Value<int?>? dureeMs,
    Value<int>? rowid,
  }) {
    return LotSynchronisationCompanion(
      idLot: idLot ?? this.idLot,
      dateReception: dateReception ?? this.dateReception,
      nombreEvenements: nombreEvenements ?? this.nombreEvenements,
      nombreAcceptes: nombreAcceptes ?? this.nombreAcceptes,
      nombreRejetes: nombreRejetes ?? this.nombreRejetes,
      dureeMs: dureeMs ?? this.dureeMs,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (idLot.present) {
      map['id_lot'] = Variable<String>(idLot.value);
    }
    if (dateReception.present) {
      map['date_reception'] = Variable<DateTime>(dateReception.value);
    }
    if (nombreEvenements.present) {
      map['nombre_evenements'] = Variable<int>(nombreEvenements.value);
    }
    if (nombreAcceptes.present) {
      map['nombre_acceptes'] = Variable<int>(nombreAcceptes.value);
    }
    if (nombreRejetes.present) {
      map['nombre_rejetes'] = Variable<int>(nombreRejetes.value);
    }
    if (dureeMs.present) {
      map['duree_ms'] = Variable<int>(dureeMs.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('LotSynchronisationCompanion(')
          ..write('idLot: $idLot, ')
          ..write('dateReception: $dateReception, ')
          ..write('nombreEvenements: $nombreEvenements, ')
          ..write('nombreAcceptes: $nombreAcceptes, ')
          ..write('nombreRejetes: $nombreRejetes, ')
          ..write('dureeMs: $dureeMs, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $ResultatEvenementTable extends ResultatEvenement
    with TableInfo<$ResultatEvenementTable, ResultatEvenementRow> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $ResultatEvenementTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idResultatMeta = const VerificationMeta(
    'idResultat',
  );
  @override
  late final GeneratedColumn<String> idResultat = GeneratedColumn<String>(
    'id_resultat',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _uuidEvenementMeta = const VerificationMeta(
    'uuidEvenement',
  );
  @override
  late final GeneratedColumn<String> uuidEvenement = GeneratedColumn<String>(
    'uuid_evenement',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _statutMeta = const VerificationMeta('statut');
  @override
  late final GeneratedColumn<String> statut = GeneratedColumn<String>(
    'statut',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _motifRejetMeta = const VerificationMeta(
    'motifRejet',
  );
  @override
  late final GeneratedColumn<String> motifRejet = GeneratedColumn<String>(
    'motif_rejet',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _lotSynchronisationIdMeta =
      const VerificationMeta('lotSynchronisationId');
  @override
  late final GeneratedColumn<String> lotSynchronisationId =
      GeneratedColumn<String>(
        'lot_synchronisation_id_lot',
        aliasedName,
        false,
        type: DriftSqlType.string,
        requiredDuringInsert: true,
      );
  @override
  List<GeneratedColumn> get $columns => [
    idResultat,
    uuidEvenement,
    statut,
    motifRejet,
    lotSynchronisationId,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'resultat_evenement';
  @override
  VerificationContext validateIntegrity(
    Insertable<ResultatEvenementRow> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id_resultat')) {
      context.handle(
        _idResultatMeta,
        idResultat.isAcceptableOrUnknown(data['id_resultat']!, _idResultatMeta),
      );
    } else if (isInserting) {
      context.missing(_idResultatMeta);
    }
    if (data.containsKey('uuid_evenement')) {
      context.handle(
        _uuidEvenementMeta,
        uuidEvenement.isAcceptableOrUnknown(
          data['uuid_evenement']!,
          _uuidEvenementMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_uuidEvenementMeta);
    }
    if (data.containsKey('statut')) {
      context.handle(
        _statutMeta,
        statut.isAcceptableOrUnknown(data['statut']!, _statutMeta),
      );
    } else if (isInserting) {
      context.missing(_statutMeta);
    }
    if (data.containsKey('motif_rejet')) {
      context.handle(
        _motifRejetMeta,
        motifRejet.isAcceptableOrUnknown(data['motif_rejet']!, _motifRejetMeta),
      );
    }
    if (data.containsKey('lot_synchronisation_id_lot')) {
      context.handle(
        _lotSynchronisationIdMeta,
        lotSynchronisationId.isAcceptableOrUnknown(
          data['lot_synchronisation_id_lot']!,
          _lotSynchronisationIdMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_lotSynchronisationIdMeta);
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {idResultat};
  @override
  ResultatEvenementRow map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return ResultatEvenementRow(
      idResultat: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}id_resultat'],
      )!,
      uuidEvenement: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}uuid_evenement'],
      )!,
      statut: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}statut'],
      )!,
      motifRejet: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}motif_rejet'],
      ),
      lotSynchronisationId: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}lot_synchronisation_id_lot'],
      )!,
    );
  }

  @override
  $ResultatEvenementTable createAlias(String alias) {
    return $ResultatEvenementTable(attachedDatabase, alias);
  }
}

class ResultatEvenementRow extends DataClass
    implements Insertable<ResultatEvenementRow> {
  final String idResultat;
  final String uuidEvenement;
  final String statut;
  final String? motifRejet;
  final String lotSynchronisationId;
  const ResultatEvenementRow({
    required this.idResultat,
    required this.uuidEvenement,
    required this.statut,
    this.motifRejet,
    required this.lotSynchronisationId,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id_resultat'] = Variable<String>(idResultat);
    map['uuid_evenement'] = Variable<String>(uuidEvenement);
    map['statut'] = Variable<String>(statut);
    if (!nullToAbsent || motifRejet != null) {
      map['motif_rejet'] = Variable<String>(motifRejet);
    }
    map['lot_synchronisation_id_lot'] = Variable<String>(lotSynchronisationId);
    return map;
  }

  ResultatEvenementCompanion toCompanion(bool nullToAbsent) {
    return ResultatEvenementCompanion(
      idResultat: Value(idResultat),
      uuidEvenement: Value(uuidEvenement),
      statut: Value(statut),
      motifRejet: motifRejet == null && nullToAbsent
          ? const Value.absent()
          : Value(motifRejet),
      lotSynchronisationId: Value(lotSynchronisationId),
    );
  }

  factory ResultatEvenementRow.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return ResultatEvenementRow(
      idResultat: serializer.fromJson<String>(json['idResultat']),
      uuidEvenement: serializer.fromJson<String>(json['uuidEvenement']),
      statut: serializer.fromJson<String>(json['statut']),
      motifRejet: serializer.fromJson<String?>(json['motifRejet']),
      lotSynchronisationId: serializer.fromJson<String>(
        json['lotSynchronisationId'],
      ),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'idResultat': serializer.toJson<String>(idResultat),
      'uuidEvenement': serializer.toJson<String>(uuidEvenement),
      'statut': serializer.toJson<String>(statut),
      'motifRejet': serializer.toJson<String?>(motifRejet),
      'lotSynchronisationId': serializer.toJson<String>(lotSynchronisationId),
    };
  }

  ResultatEvenementRow copyWith({
    String? idResultat,
    String? uuidEvenement,
    String? statut,
    Value<String?> motifRejet = const Value.absent(),
    String? lotSynchronisationId,
  }) => ResultatEvenementRow(
    idResultat: idResultat ?? this.idResultat,
    uuidEvenement: uuidEvenement ?? this.uuidEvenement,
    statut: statut ?? this.statut,
    motifRejet: motifRejet.present ? motifRejet.value : this.motifRejet,
    lotSynchronisationId: lotSynchronisationId ?? this.lotSynchronisationId,
  );
  ResultatEvenementRow copyWithCompanion(ResultatEvenementCompanion data) {
    return ResultatEvenementRow(
      idResultat: data.idResultat.present
          ? data.idResultat.value
          : this.idResultat,
      uuidEvenement: data.uuidEvenement.present
          ? data.uuidEvenement.value
          : this.uuidEvenement,
      statut: data.statut.present ? data.statut.value : this.statut,
      motifRejet: data.motifRejet.present
          ? data.motifRejet.value
          : this.motifRejet,
      lotSynchronisationId: data.lotSynchronisationId.present
          ? data.lotSynchronisationId.value
          : this.lotSynchronisationId,
    );
  }

  @override
  String toString() {
    return (StringBuffer('ResultatEvenementRow(')
          ..write('idResultat: $idResultat, ')
          ..write('uuidEvenement: $uuidEvenement, ')
          ..write('statut: $statut, ')
          ..write('motifRejet: $motifRejet, ')
          ..write('lotSynchronisationId: $lotSynchronisationId')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
    idResultat,
    uuidEvenement,
    statut,
    motifRejet,
    lotSynchronisationId,
  );
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is ResultatEvenementRow &&
          other.idResultat == this.idResultat &&
          other.uuidEvenement == this.uuidEvenement &&
          other.statut == this.statut &&
          other.motifRejet == this.motifRejet &&
          other.lotSynchronisationId == this.lotSynchronisationId);
}

class ResultatEvenementCompanion extends UpdateCompanion<ResultatEvenementRow> {
  final Value<String> idResultat;
  final Value<String> uuidEvenement;
  final Value<String> statut;
  final Value<String?> motifRejet;
  final Value<String> lotSynchronisationId;
  final Value<int> rowid;
  const ResultatEvenementCompanion({
    this.idResultat = const Value.absent(),
    this.uuidEvenement = const Value.absent(),
    this.statut = const Value.absent(),
    this.motifRejet = const Value.absent(),
    this.lotSynchronisationId = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  ResultatEvenementCompanion.insert({
    required String idResultat,
    required String uuidEvenement,
    required String statut,
    this.motifRejet = const Value.absent(),
    required String lotSynchronisationId,
    this.rowid = const Value.absent(),
  }) : idResultat = Value(idResultat),
       uuidEvenement = Value(uuidEvenement),
       statut = Value(statut),
       lotSynchronisationId = Value(lotSynchronisationId);
  static Insertable<ResultatEvenementRow> custom({
    Expression<String>? idResultat,
    Expression<String>? uuidEvenement,
    Expression<String>? statut,
    Expression<String>? motifRejet,
    Expression<String>? lotSynchronisationId,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (idResultat != null) 'id_resultat': idResultat,
      if (uuidEvenement != null) 'uuid_evenement': uuidEvenement,
      if (statut != null) 'statut': statut,
      if (motifRejet != null) 'motif_rejet': motifRejet,
      if (lotSynchronisationId != null)
        'lot_synchronisation_id_lot': lotSynchronisationId,
      if (rowid != null) 'rowid': rowid,
    });
  }

  ResultatEvenementCompanion copyWith({
    Value<String>? idResultat,
    Value<String>? uuidEvenement,
    Value<String>? statut,
    Value<String?>? motifRejet,
    Value<String>? lotSynchronisationId,
    Value<int>? rowid,
  }) {
    return ResultatEvenementCompanion(
      idResultat: idResultat ?? this.idResultat,
      uuidEvenement: uuidEvenement ?? this.uuidEvenement,
      statut: statut ?? this.statut,
      motifRejet: motifRejet ?? this.motifRejet,
      lotSynchronisationId: lotSynchronisationId ?? this.lotSynchronisationId,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (idResultat.present) {
      map['id_resultat'] = Variable<String>(idResultat.value);
    }
    if (uuidEvenement.present) {
      map['uuid_evenement'] = Variable<String>(uuidEvenement.value);
    }
    if (statut.present) {
      map['statut'] = Variable<String>(statut.value);
    }
    if (motifRejet.present) {
      map['motif_rejet'] = Variable<String>(motifRejet.value);
    }
    if (lotSynchronisationId.present) {
      map['lot_synchronisation_id_lot'] = Variable<String>(
        lotSynchronisationId.value,
      );
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('ResultatEvenementCompanion(')
          ..write('idResultat: $idResultat, ')
          ..write('uuidEvenement: $uuidEvenement, ')
          ..write('statut: $statut, ')
          ..write('motifRejet: $motifRejet, ')
          ..write('lotSynchronisationId: $lotSynchronisationId, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

abstract class _$BaseLocale extends GeneratedDatabase {
  _$BaseLocale(QueryExecutor e) : super(e);
  $BaseLocaleManager get managers => $BaseLocaleManager(this);
  late final $SessionLocaleTable sessionLocale = $SessionLocaleTable(this);
  late final $FileEnvoiTable fileEnvoi = $FileEnvoiTable(this);
  late final $CacheReferenceTable cacheReference = $CacheReferenceTable(this);
  late final $JournalLocalTable journalLocal = $JournalLocalTable(this);
  late final $LotSynchronisationTable lotSynchronisation =
      $LotSynchronisationTable(this);
  late final $ResultatEvenementTable resultatEvenement =
      $ResultatEvenementTable(this);
  @override
  Iterable<TableInfo<Table, Object?>> get allTables =>
      allSchemaEntities.whereType<TableInfo<Table, Object?>>();
  @override
  List<DatabaseSchemaEntity> get allSchemaEntities => [
    sessionLocale,
    fileEnvoi,
    cacheReference,
    journalLocal,
    lotSynchronisation,
    resultatEvenement,
  ];
}

typedef $$SessionLocaleTableCreateCompanionBuilder =
    SessionLocaleCompanion Function({
      required String idSession,
      required String identifiant,
      required String roleCode,
      Value<String?> jetonChiffre,
      required String pinHashLocal,
      required String pinSel,
      required DateTime derniereConnexionEnLigne,
      Value<int> rowid,
    });
typedef $$SessionLocaleTableUpdateCompanionBuilder =
    SessionLocaleCompanion Function({
      Value<String> idSession,
      Value<String> identifiant,
      Value<String> roleCode,
      Value<String?> jetonChiffre,
      Value<String> pinHashLocal,
      Value<String> pinSel,
      Value<DateTime> derniereConnexionEnLigne,
      Value<int> rowid,
    });

class $$SessionLocaleTableFilterComposer
    extends Composer<_$BaseLocale, $SessionLocaleTable> {
  $$SessionLocaleTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get idSession => $composableBuilder(
    column: $table.idSession,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get identifiant => $composableBuilder(
    column: $table.identifiant,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get roleCode => $composableBuilder(
    column: $table.roleCode,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get jetonChiffre => $composableBuilder(
    column: $table.jetonChiffre,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get pinHashLocal => $composableBuilder(
    column: $table.pinHashLocal,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get pinSel => $composableBuilder(
    column: $table.pinSel,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get derniereConnexionEnLigne => $composableBuilder(
    column: $table.derniereConnexionEnLigne,
    builder: (column) => ColumnFilters(column),
  );
}

class $$SessionLocaleTableOrderingComposer
    extends Composer<_$BaseLocale, $SessionLocaleTable> {
  $$SessionLocaleTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get idSession => $composableBuilder(
    column: $table.idSession,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get identifiant => $composableBuilder(
    column: $table.identifiant,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get roleCode => $composableBuilder(
    column: $table.roleCode,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get jetonChiffre => $composableBuilder(
    column: $table.jetonChiffre,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get pinHashLocal => $composableBuilder(
    column: $table.pinHashLocal,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get pinSel => $composableBuilder(
    column: $table.pinSel,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get derniereConnexionEnLigne => $composableBuilder(
    column: $table.derniereConnexionEnLigne,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$SessionLocaleTableAnnotationComposer
    extends Composer<_$BaseLocale, $SessionLocaleTable> {
  $$SessionLocaleTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get idSession =>
      $composableBuilder(column: $table.idSession, builder: (column) => column);

  GeneratedColumn<String> get identifiant => $composableBuilder(
    column: $table.identifiant,
    builder: (column) => column,
  );

  GeneratedColumn<String> get roleCode =>
      $composableBuilder(column: $table.roleCode, builder: (column) => column);

  GeneratedColumn<String> get jetonChiffre => $composableBuilder(
    column: $table.jetonChiffre,
    builder: (column) => column,
  );

  GeneratedColumn<String> get pinHashLocal => $composableBuilder(
    column: $table.pinHashLocal,
    builder: (column) => column,
  );

  GeneratedColumn<String> get pinSel =>
      $composableBuilder(column: $table.pinSel, builder: (column) => column);

  GeneratedColumn<DateTime> get derniereConnexionEnLigne => $composableBuilder(
    column: $table.derniereConnexionEnLigne,
    builder: (column) => column,
  );
}

class $$SessionLocaleTableTableManager
    extends
        RootTableManager<
          _$BaseLocale,
          $SessionLocaleTable,
          SessionLocaleRow,
          $$SessionLocaleTableFilterComposer,
          $$SessionLocaleTableOrderingComposer,
          $$SessionLocaleTableAnnotationComposer,
          $$SessionLocaleTableCreateCompanionBuilder,
          $$SessionLocaleTableUpdateCompanionBuilder,
          (
            SessionLocaleRow,
            BaseReferences<_$BaseLocale, $SessionLocaleTable, SessionLocaleRow>,
          ),
          SessionLocaleRow,
          PrefetchHooks Function()
        > {
  $$SessionLocaleTableTableManager(_$BaseLocale db, $SessionLocaleTable table)
    : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$SessionLocaleTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$SessionLocaleTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$SessionLocaleTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback:
              ({
                Value<String> idSession = const Value.absent(),
                Value<String> identifiant = const Value.absent(),
                Value<String> roleCode = const Value.absent(),
                Value<String?> jetonChiffre = const Value.absent(),
                Value<String> pinHashLocal = const Value.absent(),
                Value<String> pinSel = const Value.absent(),
                Value<DateTime> derniereConnexionEnLigne = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => SessionLocaleCompanion(
                idSession: idSession,
                identifiant: identifiant,
                roleCode: roleCode,
                jetonChiffre: jetonChiffre,
                pinHashLocal: pinHashLocal,
                pinSel: pinSel,
                derniereConnexionEnLigne: derniereConnexionEnLigne,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String idSession,
                required String identifiant,
                required String roleCode,
                Value<String?> jetonChiffre = const Value.absent(),
                required String pinHashLocal,
                required String pinSel,
                required DateTime derniereConnexionEnLigne,
                Value<int> rowid = const Value.absent(),
              }) => SessionLocaleCompanion.insert(
                idSession: idSession,
                identifiant: identifiant,
                roleCode: roleCode,
                jetonChiffre: jetonChiffre,
                pinHashLocal: pinHashLocal,
                pinSel: pinSel,
                derniereConnexionEnLigne: derniereConnexionEnLigne,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$SessionLocaleTableProcessedTableManager =
    ProcessedTableManager<
      _$BaseLocale,
      $SessionLocaleTable,
      SessionLocaleRow,
      $$SessionLocaleTableFilterComposer,
      $$SessionLocaleTableOrderingComposer,
      $$SessionLocaleTableAnnotationComposer,
      $$SessionLocaleTableCreateCompanionBuilder,
      $$SessionLocaleTableUpdateCompanionBuilder,
      (
        SessionLocaleRow,
        BaseReferences<_$BaseLocale, $SessionLocaleTable, SessionLocaleRow>,
      ),
      SessionLocaleRow,
      PrefetchHooks Function()
    >;
typedef $$FileEnvoiTableCreateCompanionBuilder =
    FileEnvoiCompanion Function({
      required String uuidEvenement,
      required String typeEvenement,
      required String chargeUtile,
      required String statut,
      Value<int> nombreTentatives,
      Value<DateTime?> prochaineTentative,
      Value<String?> sessionLocaleId,
      Value<String?> lotSynchronisationId,
      Value<int> rowid,
    });
typedef $$FileEnvoiTableUpdateCompanionBuilder =
    FileEnvoiCompanion Function({
      Value<String> uuidEvenement,
      Value<String> typeEvenement,
      Value<String> chargeUtile,
      Value<String> statut,
      Value<int> nombreTentatives,
      Value<DateTime?> prochaineTentative,
      Value<String?> sessionLocaleId,
      Value<String?> lotSynchronisationId,
      Value<int> rowid,
    });

class $$FileEnvoiTableFilterComposer
    extends Composer<_$BaseLocale, $FileEnvoiTable> {
  $$FileEnvoiTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get uuidEvenement => $composableBuilder(
    column: $table.uuidEvenement,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get typeEvenement => $composableBuilder(
    column: $table.typeEvenement,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get chargeUtile => $composableBuilder(
    column: $table.chargeUtile,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get statut => $composableBuilder(
    column: $table.statut,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get nombreTentatives => $composableBuilder(
    column: $table.nombreTentatives,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get prochaineTentative => $composableBuilder(
    column: $table.prochaineTentative,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get sessionLocaleId => $composableBuilder(
    column: $table.sessionLocaleId,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get lotSynchronisationId => $composableBuilder(
    column: $table.lotSynchronisationId,
    builder: (column) => ColumnFilters(column),
  );
}

class $$FileEnvoiTableOrderingComposer
    extends Composer<_$BaseLocale, $FileEnvoiTable> {
  $$FileEnvoiTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get uuidEvenement => $composableBuilder(
    column: $table.uuidEvenement,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get typeEvenement => $composableBuilder(
    column: $table.typeEvenement,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get chargeUtile => $composableBuilder(
    column: $table.chargeUtile,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get statut => $composableBuilder(
    column: $table.statut,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get nombreTentatives => $composableBuilder(
    column: $table.nombreTentatives,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get prochaineTentative => $composableBuilder(
    column: $table.prochaineTentative,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get sessionLocaleId => $composableBuilder(
    column: $table.sessionLocaleId,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get lotSynchronisationId => $composableBuilder(
    column: $table.lotSynchronisationId,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$FileEnvoiTableAnnotationComposer
    extends Composer<_$BaseLocale, $FileEnvoiTable> {
  $$FileEnvoiTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get uuidEvenement => $composableBuilder(
    column: $table.uuidEvenement,
    builder: (column) => column,
  );

  GeneratedColumn<String> get typeEvenement => $composableBuilder(
    column: $table.typeEvenement,
    builder: (column) => column,
  );

  GeneratedColumn<String> get chargeUtile => $composableBuilder(
    column: $table.chargeUtile,
    builder: (column) => column,
  );

  GeneratedColumn<String> get statut =>
      $composableBuilder(column: $table.statut, builder: (column) => column);

  GeneratedColumn<int> get nombreTentatives => $composableBuilder(
    column: $table.nombreTentatives,
    builder: (column) => column,
  );

  GeneratedColumn<DateTime> get prochaineTentative => $composableBuilder(
    column: $table.prochaineTentative,
    builder: (column) => column,
  );

  GeneratedColumn<String> get sessionLocaleId => $composableBuilder(
    column: $table.sessionLocaleId,
    builder: (column) => column,
  );

  GeneratedColumn<String> get lotSynchronisationId => $composableBuilder(
    column: $table.lotSynchronisationId,
    builder: (column) => column,
  );
}

class $$FileEnvoiTableTableManager
    extends
        RootTableManager<
          _$BaseLocale,
          $FileEnvoiTable,
          FileEnvoiRow,
          $$FileEnvoiTableFilterComposer,
          $$FileEnvoiTableOrderingComposer,
          $$FileEnvoiTableAnnotationComposer,
          $$FileEnvoiTableCreateCompanionBuilder,
          $$FileEnvoiTableUpdateCompanionBuilder,
          (
            FileEnvoiRow,
            BaseReferences<_$BaseLocale, $FileEnvoiTable, FileEnvoiRow>,
          ),
          FileEnvoiRow,
          PrefetchHooks Function()
        > {
  $$FileEnvoiTableTableManager(_$BaseLocale db, $FileEnvoiTable table)
    : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$FileEnvoiTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$FileEnvoiTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$FileEnvoiTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback:
              ({
                Value<String> uuidEvenement = const Value.absent(),
                Value<String> typeEvenement = const Value.absent(),
                Value<String> chargeUtile = const Value.absent(),
                Value<String> statut = const Value.absent(),
                Value<int> nombreTentatives = const Value.absent(),
                Value<DateTime?> prochaineTentative = const Value.absent(),
                Value<String?> sessionLocaleId = const Value.absent(),
                Value<String?> lotSynchronisationId = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => FileEnvoiCompanion(
                uuidEvenement: uuidEvenement,
                typeEvenement: typeEvenement,
                chargeUtile: chargeUtile,
                statut: statut,
                nombreTentatives: nombreTentatives,
                prochaineTentative: prochaineTentative,
                sessionLocaleId: sessionLocaleId,
                lotSynchronisationId: lotSynchronisationId,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String uuidEvenement,
                required String typeEvenement,
                required String chargeUtile,
                required String statut,
                Value<int> nombreTentatives = const Value.absent(),
                Value<DateTime?> prochaineTentative = const Value.absent(),
                Value<String?> sessionLocaleId = const Value.absent(),
                Value<String?> lotSynchronisationId = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => FileEnvoiCompanion.insert(
                uuidEvenement: uuidEvenement,
                typeEvenement: typeEvenement,
                chargeUtile: chargeUtile,
                statut: statut,
                nombreTentatives: nombreTentatives,
                prochaineTentative: prochaineTentative,
                sessionLocaleId: sessionLocaleId,
                lotSynchronisationId: lotSynchronisationId,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$FileEnvoiTableProcessedTableManager =
    ProcessedTableManager<
      _$BaseLocale,
      $FileEnvoiTable,
      FileEnvoiRow,
      $$FileEnvoiTableFilterComposer,
      $$FileEnvoiTableOrderingComposer,
      $$FileEnvoiTableAnnotationComposer,
      $$FileEnvoiTableCreateCompanionBuilder,
      $$FileEnvoiTableUpdateCompanionBuilder,
      (
        FileEnvoiRow,
        BaseReferences<_$BaseLocale, $FileEnvoiTable, FileEnvoiRow>,
      ),
      FileEnvoiRow,
      PrefetchHooks Function()
    >;
typedef $$CacheReferenceTableCreateCompanionBuilder =
    CacheReferenceCompanion Function({
      required String typeDonnee,
      required String cle,
      required String contenu,
      required int version,
      Value<int> rowid,
    });
typedef $$CacheReferenceTableUpdateCompanionBuilder =
    CacheReferenceCompanion Function({
      Value<String> typeDonnee,
      Value<String> cle,
      Value<String> contenu,
      Value<int> version,
      Value<int> rowid,
    });

class $$CacheReferenceTableFilterComposer
    extends Composer<_$BaseLocale, $CacheReferenceTable> {
  $$CacheReferenceTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get typeDonnee => $composableBuilder(
    column: $table.typeDonnee,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get cle => $composableBuilder(
    column: $table.cle,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get contenu => $composableBuilder(
    column: $table.contenu,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get version => $composableBuilder(
    column: $table.version,
    builder: (column) => ColumnFilters(column),
  );
}

class $$CacheReferenceTableOrderingComposer
    extends Composer<_$BaseLocale, $CacheReferenceTable> {
  $$CacheReferenceTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get typeDonnee => $composableBuilder(
    column: $table.typeDonnee,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get cle => $composableBuilder(
    column: $table.cle,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get contenu => $composableBuilder(
    column: $table.contenu,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get version => $composableBuilder(
    column: $table.version,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$CacheReferenceTableAnnotationComposer
    extends Composer<_$BaseLocale, $CacheReferenceTable> {
  $$CacheReferenceTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get typeDonnee => $composableBuilder(
    column: $table.typeDonnee,
    builder: (column) => column,
  );

  GeneratedColumn<String> get cle =>
      $composableBuilder(column: $table.cle, builder: (column) => column);

  GeneratedColumn<String> get contenu =>
      $composableBuilder(column: $table.contenu, builder: (column) => column);

  GeneratedColumn<int> get version =>
      $composableBuilder(column: $table.version, builder: (column) => column);
}

class $$CacheReferenceTableTableManager
    extends
        RootTableManager<
          _$BaseLocale,
          $CacheReferenceTable,
          CacheReferenceRow,
          $$CacheReferenceTableFilterComposer,
          $$CacheReferenceTableOrderingComposer,
          $$CacheReferenceTableAnnotationComposer,
          $$CacheReferenceTableCreateCompanionBuilder,
          $$CacheReferenceTableUpdateCompanionBuilder,
          (
            CacheReferenceRow,
            BaseReferences<
              _$BaseLocale,
              $CacheReferenceTable,
              CacheReferenceRow
            >,
          ),
          CacheReferenceRow,
          PrefetchHooks Function()
        > {
  $$CacheReferenceTableTableManager(_$BaseLocale db, $CacheReferenceTable table)
    : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$CacheReferenceTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$CacheReferenceTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$CacheReferenceTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback:
              ({
                Value<String> typeDonnee = const Value.absent(),
                Value<String> cle = const Value.absent(),
                Value<String> contenu = const Value.absent(),
                Value<int> version = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => CacheReferenceCompanion(
                typeDonnee: typeDonnee,
                cle: cle,
                contenu: contenu,
                version: version,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String typeDonnee,
                required String cle,
                required String contenu,
                required int version,
                Value<int> rowid = const Value.absent(),
              }) => CacheReferenceCompanion.insert(
                typeDonnee: typeDonnee,
                cle: cle,
                contenu: contenu,
                version: version,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$CacheReferenceTableProcessedTableManager =
    ProcessedTableManager<
      _$BaseLocale,
      $CacheReferenceTable,
      CacheReferenceRow,
      $$CacheReferenceTableFilterComposer,
      $$CacheReferenceTableOrderingComposer,
      $$CacheReferenceTableAnnotationComposer,
      $$CacheReferenceTableCreateCompanionBuilder,
      $$CacheReferenceTableUpdateCompanionBuilder,
      (
        CacheReferenceRow,
        BaseReferences<_$BaseLocale, $CacheReferenceTable, CacheReferenceRow>,
      ),
      CacheReferenceRow,
      PrefetchHooks Function()
    >;
typedef $$JournalLocalTableCreateCompanionBuilder =
    JournalLocalCompanion Function({
      required String idEntree,
      required String evenement,
      required DateTime horodatage,
      Value<String?> sessionLocaleId,
      Value<int> rowid,
    });
typedef $$JournalLocalTableUpdateCompanionBuilder =
    JournalLocalCompanion Function({
      Value<String> idEntree,
      Value<String> evenement,
      Value<DateTime> horodatage,
      Value<String?> sessionLocaleId,
      Value<int> rowid,
    });

class $$JournalLocalTableFilterComposer
    extends Composer<_$BaseLocale, $JournalLocalTable> {
  $$JournalLocalTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get idEntree => $composableBuilder(
    column: $table.idEntree,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get evenement => $composableBuilder(
    column: $table.evenement,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get horodatage => $composableBuilder(
    column: $table.horodatage,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get sessionLocaleId => $composableBuilder(
    column: $table.sessionLocaleId,
    builder: (column) => ColumnFilters(column),
  );
}

class $$JournalLocalTableOrderingComposer
    extends Composer<_$BaseLocale, $JournalLocalTable> {
  $$JournalLocalTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get idEntree => $composableBuilder(
    column: $table.idEntree,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get evenement => $composableBuilder(
    column: $table.evenement,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get horodatage => $composableBuilder(
    column: $table.horodatage,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get sessionLocaleId => $composableBuilder(
    column: $table.sessionLocaleId,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$JournalLocalTableAnnotationComposer
    extends Composer<_$BaseLocale, $JournalLocalTable> {
  $$JournalLocalTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get idEntree =>
      $composableBuilder(column: $table.idEntree, builder: (column) => column);

  GeneratedColumn<String> get evenement =>
      $composableBuilder(column: $table.evenement, builder: (column) => column);

  GeneratedColumn<DateTime> get horodatage => $composableBuilder(
    column: $table.horodatage,
    builder: (column) => column,
  );

  GeneratedColumn<String> get sessionLocaleId => $composableBuilder(
    column: $table.sessionLocaleId,
    builder: (column) => column,
  );
}

class $$JournalLocalTableTableManager
    extends
        RootTableManager<
          _$BaseLocale,
          $JournalLocalTable,
          JournalLocalRow,
          $$JournalLocalTableFilterComposer,
          $$JournalLocalTableOrderingComposer,
          $$JournalLocalTableAnnotationComposer,
          $$JournalLocalTableCreateCompanionBuilder,
          $$JournalLocalTableUpdateCompanionBuilder,
          (
            JournalLocalRow,
            BaseReferences<_$BaseLocale, $JournalLocalTable, JournalLocalRow>,
          ),
          JournalLocalRow,
          PrefetchHooks Function()
        > {
  $$JournalLocalTableTableManager(_$BaseLocale db, $JournalLocalTable table)
    : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$JournalLocalTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$JournalLocalTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$JournalLocalTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback:
              ({
                Value<String> idEntree = const Value.absent(),
                Value<String> evenement = const Value.absent(),
                Value<DateTime> horodatage = const Value.absent(),
                Value<String?> sessionLocaleId = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => JournalLocalCompanion(
                idEntree: idEntree,
                evenement: evenement,
                horodatage: horodatage,
                sessionLocaleId: sessionLocaleId,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String idEntree,
                required String evenement,
                required DateTime horodatage,
                Value<String?> sessionLocaleId = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => JournalLocalCompanion.insert(
                idEntree: idEntree,
                evenement: evenement,
                horodatage: horodatage,
                sessionLocaleId: sessionLocaleId,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$JournalLocalTableProcessedTableManager =
    ProcessedTableManager<
      _$BaseLocale,
      $JournalLocalTable,
      JournalLocalRow,
      $$JournalLocalTableFilterComposer,
      $$JournalLocalTableOrderingComposer,
      $$JournalLocalTableAnnotationComposer,
      $$JournalLocalTableCreateCompanionBuilder,
      $$JournalLocalTableUpdateCompanionBuilder,
      (
        JournalLocalRow,
        BaseReferences<_$BaseLocale, $JournalLocalTable, JournalLocalRow>,
      ),
      JournalLocalRow,
      PrefetchHooks Function()
    >;
typedef $$LotSynchronisationTableCreateCompanionBuilder =
    LotSynchronisationCompanion Function({
      required String idLot,
      Value<DateTime?> dateReception,
      Value<int> nombreEvenements,
      Value<int> nombreAcceptes,
      Value<int> nombreRejetes,
      Value<int?> dureeMs,
      Value<int> rowid,
    });
typedef $$LotSynchronisationTableUpdateCompanionBuilder =
    LotSynchronisationCompanion Function({
      Value<String> idLot,
      Value<DateTime?> dateReception,
      Value<int> nombreEvenements,
      Value<int> nombreAcceptes,
      Value<int> nombreRejetes,
      Value<int?> dureeMs,
      Value<int> rowid,
    });

class $$LotSynchronisationTableFilterComposer
    extends Composer<_$BaseLocale, $LotSynchronisationTable> {
  $$LotSynchronisationTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get idLot => $composableBuilder(
    column: $table.idLot,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get dateReception => $composableBuilder(
    column: $table.dateReception,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get nombreEvenements => $composableBuilder(
    column: $table.nombreEvenements,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get nombreAcceptes => $composableBuilder(
    column: $table.nombreAcceptes,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get nombreRejetes => $composableBuilder(
    column: $table.nombreRejetes,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get dureeMs => $composableBuilder(
    column: $table.dureeMs,
    builder: (column) => ColumnFilters(column),
  );
}

class $$LotSynchronisationTableOrderingComposer
    extends Composer<_$BaseLocale, $LotSynchronisationTable> {
  $$LotSynchronisationTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get idLot => $composableBuilder(
    column: $table.idLot,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get dateReception => $composableBuilder(
    column: $table.dateReception,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get nombreEvenements => $composableBuilder(
    column: $table.nombreEvenements,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get nombreAcceptes => $composableBuilder(
    column: $table.nombreAcceptes,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get nombreRejetes => $composableBuilder(
    column: $table.nombreRejetes,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get dureeMs => $composableBuilder(
    column: $table.dureeMs,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$LotSynchronisationTableAnnotationComposer
    extends Composer<_$BaseLocale, $LotSynchronisationTable> {
  $$LotSynchronisationTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get idLot =>
      $composableBuilder(column: $table.idLot, builder: (column) => column);

  GeneratedColumn<DateTime> get dateReception => $composableBuilder(
    column: $table.dateReception,
    builder: (column) => column,
  );

  GeneratedColumn<int> get nombreEvenements => $composableBuilder(
    column: $table.nombreEvenements,
    builder: (column) => column,
  );

  GeneratedColumn<int> get nombreAcceptes => $composableBuilder(
    column: $table.nombreAcceptes,
    builder: (column) => column,
  );

  GeneratedColumn<int> get nombreRejetes => $composableBuilder(
    column: $table.nombreRejetes,
    builder: (column) => column,
  );

  GeneratedColumn<int> get dureeMs =>
      $composableBuilder(column: $table.dureeMs, builder: (column) => column);
}

class $$LotSynchronisationTableTableManager
    extends
        RootTableManager<
          _$BaseLocale,
          $LotSynchronisationTable,
          LotSynchronisationRow,
          $$LotSynchronisationTableFilterComposer,
          $$LotSynchronisationTableOrderingComposer,
          $$LotSynchronisationTableAnnotationComposer,
          $$LotSynchronisationTableCreateCompanionBuilder,
          $$LotSynchronisationTableUpdateCompanionBuilder,
          (
            LotSynchronisationRow,
            BaseReferences<
              _$BaseLocale,
              $LotSynchronisationTable,
              LotSynchronisationRow
            >,
          ),
          LotSynchronisationRow,
          PrefetchHooks Function()
        > {
  $$LotSynchronisationTableTableManager(
    _$BaseLocale db,
    $LotSynchronisationTable table,
  ) : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$LotSynchronisationTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$LotSynchronisationTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$LotSynchronisationTableAnnotationComposer(
                $db: db,
                $table: table,
              ),
          updateCompanionCallback:
              ({
                Value<String> idLot = const Value.absent(),
                Value<DateTime?> dateReception = const Value.absent(),
                Value<int> nombreEvenements = const Value.absent(),
                Value<int> nombreAcceptes = const Value.absent(),
                Value<int> nombreRejetes = const Value.absent(),
                Value<int?> dureeMs = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => LotSynchronisationCompanion(
                idLot: idLot,
                dateReception: dateReception,
                nombreEvenements: nombreEvenements,
                nombreAcceptes: nombreAcceptes,
                nombreRejetes: nombreRejetes,
                dureeMs: dureeMs,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String idLot,
                Value<DateTime?> dateReception = const Value.absent(),
                Value<int> nombreEvenements = const Value.absent(),
                Value<int> nombreAcceptes = const Value.absent(),
                Value<int> nombreRejetes = const Value.absent(),
                Value<int?> dureeMs = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => LotSynchronisationCompanion.insert(
                idLot: idLot,
                dateReception: dateReception,
                nombreEvenements: nombreEvenements,
                nombreAcceptes: nombreAcceptes,
                nombreRejetes: nombreRejetes,
                dureeMs: dureeMs,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$LotSynchronisationTableProcessedTableManager =
    ProcessedTableManager<
      _$BaseLocale,
      $LotSynchronisationTable,
      LotSynchronisationRow,
      $$LotSynchronisationTableFilterComposer,
      $$LotSynchronisationTableOrderingComposer,
      $$LotSynchronisationTableAnnotationComposer,
      $$LotSynchronisationTableCreateCompanionBuilder,
      $$LotSynchronisationTableUpdateCompanionBuilder,
      (
        LotSynchronisationRow,
        BaseReferences<
          _$BaseLocale,
          $LotSynchronisationTable,
          LotSynchronisationRow
        >,
      ),
      LotSynchronisationRow,
      PrefetchHooks Function()
    >;
typedef $$ResultatEvenementTableCreateCompanionBuilder =
    ResultatEvenementCompanion Function({
      required String idResultat,
      required String uuidEvenement,
      required String statut,
      Value<String?> motifRejet,
      required String lotSynchronisationId,
      Value<int> rowid,
    });
typedef $$ResultatEvenementTableUpdateCompanionBuilder =
    ResultatEvenementCompanion Function({
      Value<String> idResultat,
      Value<String> uuidEvenement,
      Value<String> statut,
      Value<String?> motifRejet,
      Value<String> lotSynchronisationId,
      Value<int> rowid,
    });

class $$ResultatEvenementTableFilterComposer
    extends Composer<_$BaseLocale, $ResultatEvenementTable> {
  $$ResultatEvenementTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get idResultat => $composableBuilder(
    column: $table.idResultat,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get uuidEvenement => $composableBuilder(
    column: $table.uuidEvenement,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get statut => $composableBuilder(
    column: $table.statut,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get motifRejet => $composableBuilder(
    column: $table.motifRejet,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get lotSynchronisationId => $composableBuilder(
    column: $table.lotSynchronisationId,
    builder: (column) => ColumnFilters(column),
  );
}

class $$ResultatEvenementTableOrderingComposer
    extends Composer<_$BaseLocale, $ResultatEvenementTable> {
  $$ResultatEvenementTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get idResultat => $composableBuilder(
    column: $table.idResultat,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get uuidEvenement => $composableBuilder(
    column: $table.uuidEvenement,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get statut => $composableBuilder(
    column: $table.statut,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get motifRejet => $composableBuilder(
    column: $table.motifRejet,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get lotSynchronisationId => $composableBuilder(
    column: $table.lotSynchronisationId,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$ResultatEvenementTableAnnotationComposer
    extends Composer<_$BaseLocale, $ResultatEvenementTable> {
  $$ResultatEvenementTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get idResultat => $composableBuilder(
    column: $table.idResultat,
    builder: (column) => column,
  );

  GeneratedColumn<String> get uuidEvenement => $composableBuilder(
    column: $table.uuidEvenement,
    builder: (column) => column,
  );

  GeneratedColumn<String> get statut =>
      $composableBuilder(column: $table.statut, builder: (column) => column);

  GeneratedColumn<String> get motifRejet => $composableBuilder(
    column: $table.motifRejet,
    builder: (column) => column,
  );

  GeneratedColumn<String> get lotSynchronisationId => $composableBuilder(
    column: $table.lotSynchronisationId,
    builder: (column) => column,
  );
}

class $$ResultatEvenementTableTableManager
    extends
        RootTableManager<
          _$BaseLocale,
          $ResultatEvenementTable,
          ResultatEvenementRow,
          $$ResultatEvenementTableFilterComposer,
          $$ResultatEvenementTableOrderingComposer,
          $$ResultatEvenementTableAnnotationComposer,
          $$ResultatEvenementTableCreateCompanionBuilder,
          $$ResultatEvenementTableUpdateCompanionBuilder,
          (
            ResultatEvenementRow,
            BaseReferences<
              _$BaseLocale,
              $ResultatEvenementTable,
              ResultatEvenementRow
            >,
          ),
          ResultatEvenementRow,
          PrefetchHooks Function()
        > {
  $$ResultatEvenementTableTableManager(
    _$BaseLocale db,
    $ResultatEvenementTable table,
  ) : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$ResultatEvenementTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$ResultatEvenementTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$ResultatEvenementTableAnnotationComposer(
                $db: db,
                $table: table,
              ),
          updateCompanionCallback:
              ({
                Value<String> idResultat = const Value.absent(),
                Value<String> uuidEvenement = const Value.absent(),
                Value<String> statut = const Value.absent(),
                Value<String?> motifRejet = const Value.absent(),
                Value<String> lotSynchronisationId = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => ResultatEvenementCompanion(
                idResultat: idResultat,
                uuidEvenement: uuidEvenement,
                statut: statut,
                motifRejet: motifRejet,
                lotSynchronisationId: lotSynchronisationId,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String idResultat,
                required String uuidEvenement,
                required String statut,
                Value<String?> motifRejet = const Value.absent(),
                required String lotSynchronisationId,
                Value<int> rowid = const Value.absent(),
              }) => ResultatEvenementCompanion.insert(
                idResultat: idResultat,
                uuidEvenement: uuidEvenement,
                statut: statut,
                motifRejet: motifRejet,
                lotSynchronisationId: lotSynchronisationId,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$ResultatEvenementTableProcessedTableManager =
    ProcessedTableManager<
      _$BaseLocale,
      $ResultatEvenementTable,
      ResultatEvenementRow,
      $$ResultatEvenementTableFilterComposer,
      $$ResultatEvenementTableOrderingComposer,
      $$ResultatEvenementTableAnnotationComposer,
      $$ResultatEvenementTableCreateCompanionBuilder,
      $$ResultatEvenementTableUpdateCompanionBuilder,
      (
        ResultatEvenementRow,
        BaseReferences<
          _$BaseLocale,
          $ResultatEvenementTable,
          ResultatEvenementRow
        >,
      ),
      ResultatEvenementRow,
      PrefetchHooks Function()
    >;

class $BaseLocaleManager {
  final _$BaseLocale _db;
  $BaseLocaleManager(this._db);
  $$SessionLocaleTableTableManager get sessionLocale =>
      $$SessionLocaleTableTableManager(_db, _db.sessionLocale);
  $$FileEnvoiTableTableManager get fileEnvoi =>
      $$FileEnvoiTableTableManager(_db, _db.fileEnvoi);
  $$CacheReferenceTableTableManager get cacheReference =>
      $$CacheReferenceTableTableManager(_db, _db.cacheReference);
  $$JournalLocalTableTableManager get journalLocal =>
      $$JournalLocalTableTableManager(_db, _db.journalLocal);
  $$LotSynchronisationTableTableManager get lotSynchronisation =>
      $$LotSynchronisationTableTableManager(_db, _db.lotSynchronisation);
  $$ResultatEvenementTableTableManager get resultatEvenement =>
      $$ResultatEvenementTableTableManager(_db, _db.resultatEvenement);
}
