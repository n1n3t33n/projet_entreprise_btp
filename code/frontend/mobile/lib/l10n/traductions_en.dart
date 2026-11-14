// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'traductions.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class TraductionsEn extends Traductions {
  TraductionsEn([String locale = 'en']) : super(locale);

  @override
  String get ongletStock => 'Stock';

  @override
  String get ongletFiches => 'Tasks';

  @override
  String get ongletAValider => 'To approve';

  @override
  String get ongletHistorique => 'History';

  @override
  String get ongletSynchro => 'Sync';

  @override
  String get ongletProfil => 'Profile';

  @override
  String get roleMagasinier => 'Storekeeper';

  @override
  String get roleTechnicien => 'Technician';

  @override
  String get roleChefChantier => 'Site manager';

  @override
  String get roleGestionnaireStock => 'Stock controller';

  @override
  String get roleResponsableTechnique => 'Technical lead';

  @override
  String get annuler => 'Cancel';

  @override
  String get changer => 'Switch';

  @override
  String get seConnecter => 'Sign in';

  @override
  String get synchroniser => 'Sync';

  @override
  String get diminuer => 'Decrease';

  @override
  String get augmenter => 'Increase';

  @override
  String get champObligatoire => 'This field is required.';

  @override
  String get modeHorsLigneSecurise => 'SECURE OFFLINE MODE';

  @override
  String get pinTitre => 'SITE PIN CODE';

  @override
  String get pinAide => 'Enter your 6-digit code';

  @override
  String get pinIncorrect => 'Wrong code. Try again.';

  @override
  String get pinIncomplet => 'The code has 6 digits.';

  @override
  String get pinRaz => 'Clear';

  @override
  String get pinEffacer => 'Delete last digit';

  @override
  String pinSaisi(int remplis, int total) {
    return '$remplis of $total digits entered';
  }

  @override
  String get deverrouillageActif => 'Offline unlock is active';

  @override
  String get donneesSurAppareil => 'Data secured on this device';

  @override
  String donneesSynchroniseesLe(String date) {
    return 'Last online sign-in: $date';
  }

  @override
  String get piedHorsLigne => 'ChantierSync · Offline mode';

  @override
  String appareil(String id) {
    return 'Device $id';
  }

  @override
  String get retirerCompteTitre => 'Remove this account from the device?';

  @override
  String get retirerCompteTexte =>
      'The data saved on this device will be erased. You will need to sign in online to come back.';

  @override
  String get retirerCompteAction => 'Remove account';

  @override
  String retirerCompteAlerte(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: 'Warning: $n entries have not been sent yet and will be lost.',
      one: 'Warning: 1 entry has not been sent yet and will be lost.',
    );
    return '$_temp0';
  }

  @override
  String get connexionAccroche =>
      'The site in your pocket, even with no network.';

  @override
  String get identifiant => 'Username';

  @override
  String get motDePasse => 'Password';

  @override
  String get afficherMotDePasse => 'Show password';

  @override
  String get masquerMotDePasse => 'Hide password';

  @override
  String get connexionAide =>
      'Online sign-in is needed only once, then you use your PIN code.';

  @override
  String get comptesDemoTitre => 'Demo accounts';

  @override
  String get comptesDemoAide =>
      'Shown only because the data is simulated. Tap a profile to fill in the form.';

  @override
  String get erreurIdentifiants => 'Wrong username or password.';

  @override
  String get erreurCompteInactif =>
      'This account is disabled. Contact your administrator.';

  @override
  String erreurVerrouille(int secondes) {
    String _temp0 = intl.Intl.pluralLogic(
      secondes,
      locale: localeName,
      other: 'Account locked. Try again in $secondes seconds.',
      one: 'Account locked. Try again in 1 second.',
      zero: 'Account temporarily locked after several failed attempts.',
    );
    return '$_temp0';
  }

  @override
  String get erreurSansAccesTerrain =>
      'This account has no field access on the mobile app.';

  @override
  String get infoSessionRevoquee => 'The account was removed from this device.';

  @override
  String get infoSessionExpiree =>
      'More than 14 days without an online sign-in: sign in again to continue.';

  @override
  String get erreurDonneesInaccessibles =>
      'Unable to open the data on this device.';

  @override
  String get erreurConnexionImpossible =>
      'Unable to connect. Check the network and try again.';

  @override
  String get definirCodeTitre => 'Set my code';

  @override
  String get definirCodeSousTitre => 'To open the app with no network';

  @override
  String get choisirCode => 'Choose a code';

  @override
  String get choisirCodeAide => '6 digits that only you will know.';

  @override
  String get confirmerCode => 'Confirm the code';

  @override
  String get confirmerCodeAide => 'Enter the same code again.';

  @override
  String get codesDifferents => 'The two codes do not match. Start again.';

  @override
  String get synchroAJour => 'Data up to date';

  @override
  String synchroEnAttente(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n items waiting to be sent',
      one: '1 item waiting to be sent',
    );
    return '$_temp0';
  }

  @override
  String get synchroTitre => 'Synchronisation';

  @override
  String get synchroExplication =>
      'Your entries are saved on the device and are sent as soon as the connection is back.';

  @override
  String get fileAttenteTitre => 'Queue';

  @override
  String get fileVideTitre => 'Nothing to send';

  @override
  String get fileVideTexte =>
      'Entries made with no network will appear here until they are sent.';

  @override
  String get etatEnAttenteEnvoi => 'Waiting';

  @override
  String get etatEnvoye => 'Sent';

  @override
  String get signatureTitre => 'Sign with your PIN code';

  @override
  String get signatureAide => 'Your code confirms the decision.';

  @override
  String get moduleEnPreparation => 'This area is being set up.';

  @override
  String get profilLangue => 'Language';

  @override
  String get profilTheme => 'Appearance';

  @override
  String get themeSysteme => 'Automatic';

  @override
  String get themeClair => 'Light';

  @override
  String get themeSombre => 'Dark';

  @override
  String get profilSynchroAide => 'Queue and sending status';

  @override
  String get profilVerrouiller => 'Lock';

  @override
  String get profilVerrouillerAide => 'Go back to the PIN code screen';

  @override
  String get profilRetirerAide => 'Erases the data on this device';

  @override
  String profilAPropos(String appareil) {
    return 'Schiavone Group · Italia Construction\nDevice $appareil · version 1.0';
  }
}
