import '../securite/coffre.dart';
import 'preferences.dart';

/// Préférences d'affichage conservées dans le coffre de l'appareil.
class DepotPreferencesCoffre implements DepotPreferences {
  const DepotPreferencesCoffre(this._coffre);

  final Coffre _coffre;

  @override
  Future<Preferences> lire() async {
    return Preferences(
      langue: CodagePreferences.langueDepuis(
        await _coffre.lireReglage('langue'),
      ),
      theme: CodagePreferences.themeDepuis(await _coffre.lireReglage('theme')),
    );
  }

  @override
  Future<void> enregistrer(Preferences preferences) async {
    await _coffre.ecrireReglage('langue', preferences.langue.languageCode);
    await _coffre.ecrireReglage('theme', preferences.theme.name);
  }
}
