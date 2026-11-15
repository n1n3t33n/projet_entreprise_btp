import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Langues proposées : le français est la référence, l'anglais et l'italien
/// en sont traduits.
const List<Locale> languesDisponibles = [
  Locale('fr'),
  Locale('en'),
  Locale('it'),
];

/// Préférences d'affichage de l'utilisateur sur cet appareil.
@immutable
class Preferences {
  const Preferences({
    this.langue = const Locale('fr'),
    this.theme = ThemeMode.system,
  });

  final Locale langue;
  final ThemeMode theme;

  Preferences copyWith({Locale? langue, ThemeMode? theme}) {
    return Preferences(
      langue: langue ?? this.langue,
      theme: theme ?? this.theme,
    );
  }
}

/// Lecture et écriture durable des préférences. L'application fournit une
/// implémentation adossée au coffre de l'appareil ; les tests, une mémoire.
abstract interface class DepotPreferences {
  Future<Preferences> lire();

  Future<void> enregistrer(Preferences preferences);
}

class DepotPreferencesMemoire implements DepotPreferences {
  DepotPreferencesMemoire([this._valeur = const Preferences()]);

  Preferences _valeur;

  @override
  Future<Preferences> lire() async => _valeur;

  @override
  Future<void> enregistrer(Preferences preferences) async =>
      _valeur = preferences;
}

/// Convertit les préférences vers et depuis leur forme enregistrée.
abstract final class CodagePreferences {
  static Locale langueDepuis(String? code) {
    return languesDisponibles.firstWhere(
      (langue) => langue.languageCode == code,
      orElse: () => languesDisponibles.first,
    );
  }

  static ThemeMode themeDepuis(String? code) {
    return ThemeMode.values.firstWhere(
      (mode) => mode.name == code,
      orElse: () => ThemeMode.system,
    );
  }
}

final depotPreferencesProvider = Provider<DepotPreferences>(
  (ref) => DepotPreferencesMemoire(),
);

/// Préférences lues au démarrage (surchargées dans `main.dart`) pour que le
/// premier affichage soit déjà dans la bonne langue et le bon thème.
final preferencesInitialesProvider = Provider<Preferences>(
  (ref) => const Preferences(),
);

class ControleurPreferences extends Notifier<Preferences> {
  @override
  Preferences build() => ref.read(preferencesInitialesProvider);

  Future<void> definirLangue(Locale langue) =>
      _appliquer(state.copyWith(langue: langue));

  Future<void> definirTheme(ThemeMode theme) =>
      _appliquer(state.copyWith(theme: theme));

  Future<void> _appliquer(Preferences suivantes) async {
    state = suivantes;
    await ref.read(depotPreferencesProvider).enregistrer(suivantes);
  }
}

final preferencesProvider =
    NotifierProvider<ControleurPreferences, Preferences>(
      ControleurPreferences.new,
    );
