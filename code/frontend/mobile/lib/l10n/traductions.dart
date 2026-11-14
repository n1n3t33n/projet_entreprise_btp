import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'traductions_en.dart';
import 'traductions_fr.dart';
import 'traductions_it.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of Traductions
/// returned by `Traductions.of(context)`.
///
/// Applications need to include `Traductions.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'l10n/traductions.dart';
///
/// return MaterialApp(
///   localizationsDelegates: Traductions.localizationsDelegates,
///   supportedLocales: Traductions.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the Traductions.supportedLocales
/// property.
abstract class Traductions {
  Traductions(String locale)
    : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static Traductions of(BuildContext context) {
    return Localizations.of<Traductions>(context, Traductions)!;
  }

  static const LocalizationsDelegate<Traductions> delegate =
      _TraductionsDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates =
      <LocalizationsDelegate<dynamic>>[
        delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
      ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[
    Locale('en'),
    Locale('fr'),
    Locale('it'),
  ];

  /// No description provided for @ongletStock.
  ///
  /// In fr, this message translates to:
  /// **'Stock'**
  String get ongletStock;

  /// No description provided for @ongletFiches.
  ///
  /// In fr, this message translates to:
  /// **'Fiches'**
  String get ongletFiches;

  /// No description provided for @ongletAValider.
  ///
  /// In fr, this message translates to:
  /// **'À valider'**
  String get ongletAValider;

  /// No description provided for @ongletHistorique.
  ///
  /// In fr, this message translates to:
  /// **'Historique'**
  String get ongletHistorique;

  /// No description provided for @ongletSynchro.
  ///
  /// In fr, this message translates to:
  /// **'Synchro'**
  String get ongletSynchro;

  /// No description provided for @ongletProfil.
  ///
  /// In fr, this message translates to:
  /// **'Profil'**
  String get ongletProfil;

  /// No description provided for @roleMagasinier.
  ///
  /// In fr, this message translates to:
  /// **'Magasinier'**
  String get roleMagasinier;

  /// No description provided for @roleTechnicien.
  ///
  /// In fr, this message translates to:
  /// **'Technicien'**
  String get roleTechnicien;

  /// No description provided for @roleChefChantier.
  ///
  /// In fr, this message translates to:
  /// **'Chef de chantier'**
  String get roleChefChantier;

  /// No description provided for @roleGestionnaireStock.
  ///
  /// In fr, this message translates to:
  /// **'Gestionnaire de stock'**
  String get roleGestionnaireStock;

  /// No description provided for @roleResponsableTechnique.
  ///
  /// In fr, this message translates to:
  /// **'Responsable technique'**
  String get roleResponsableTechnique;

  /// No description provided for @annuler.
  ///
  /// In fr, this message translates to:
  /// **'Annuler'**
  String get annuler;

  /// No description provided for @changer.
  ///
  /// In fr, this message translates to:
  /// **'Changer'**
  String get changer;

  /// No description provided for @seConnecter.
  ///
  /// In fr, this message translates to:
  /// **'Se connecter'**
  String get seConnecter;

  /// No description provided for @synchroniser.
  ///
  /// In fr, this message translates to:
  /// **'Synchroniser'**
  String get synchroniser;

  /// No description provided for @diminuer.
  ///
  /// In fr, this message translates to:
  /// **'Diminuer'**
  String get diminuer;

  /// No description provided for @augmenter.
  ///
  /// In fr, this message translates to:
  /// **'Augmenter'**
  String get augmenter;

  /// No description provided for @champObligatoire.
  ///
  /// In fr, this message translates to:
  /// **'Ce champ est obligatoire.'**
  String get champObligatoire;

  /// No description provided for @modeHorsLigneSecurise.
  ///
  /// In fr, this message translates to:
  /// **'MODE HORS-LIGNE SÉCURISÉ'**
  String get modeHorsLigneSecurise;

  /// No description provided for @pinTitre.
  ///
  /// In fr, this message translates to:
  /// **'CODE PIN CHANTIER'**
  String get pinTitre;

  /// No description provided for @pinAide.
  ///
  /// In fr, this message translates to:
  /// **'Saisissez votre code à 6 chiffres'**
  String get pinAide;

  /// No description provided for @pinIncorrect.
  ///
  /// In fr, this message translates to:
  /// **'Code incorrect. Réessayez.'**
  String get pinIncorrect;

  /// No description provided for @pinIncomplet.
  ///
  /// In fr, this message translates to:
  /// **'Le code compte 6 chiffres.'**
  String get pinIncomplet;

  /// No description provided for @pinRaz.
  ///
  /// In fr, this message translates to:
  /// **'Vider'**
  String get pinRaz;

  /// No description provided for @pinEffacer.
  ///
  /// In fr, this message translates to:
  /// **'Effacer le dernier chiffre'**
  String get pinEffacer;

  /// No description provided for @pinSaisi.
  ///
  /// In fr, this message translates to:
  /// **'{remplis} chiffres saisis sur {total}'**
  String pinSaisi(int remplis, int total);

  /// No description provided for @deverrouillageActif.
  ///
  /// In fr, this message translates to:
  /// **'Déverrouillage hors-ligne actif'**
  String get deverrouillageActif;

  /// No description provided for @donneesSurAppareil.
  ///
  /// In fr, this message translates to:
  /// **'Données sécurisées sur l\'appareil'**
  String get donneesSurAppareil;

  /// No description provided for @donneesSynchroniseesLe.
  ///
  /// In fr, this message translates to:
  /// **'Dernière connexion en ligne : {date}'**
  String donneesSynchroniseesLe(String date);

  /// No description provided for @piedHorsLigne.
  ///
  /// In fr, this message translates to:
  /// **'ChantierSync · Mode hors-ligne'**
  String get piedHorsLigne;

  /// No description provided for @appareil.
  ///
  /// In fr, this message translates to:
  /// **'Appareil {id}'**
  String appareil(String id);

  /// No description provided for @retirerCompteTitre.
  ///
  /// In fr, this message translates to:
  /// **'Retirer ce compte de l\'appareil ?'**
  String get retirerCompteTitre;

  /// No description provided for @retirerCompteTexte.
  ///
  /// In fr, this message translates to:
  /// **'Les données enregistrées sur cet appareil seront effacées. Une connexion en ligne sera nécessaire pour revenir.'**
  String get retirerCompteTexte;

  /// No description provided for @retirerCompteAction.
  ///
  /// In fr, this message translates to:
  /// **'Retirer le compte'**
  String get retirerCompteAction;

  /// No description provided for @retirerCompteAlerte.
  ///
  /// In fr, this message translates to:
  /// **'{n, plural, =1{Attention : 1 saisie n\'a pas encore été envoyée et sera perdue.} other{Attention : {n} saisies n\'ont pas encore été envoyées et seront perdues.}}'**
  String retirerCompteAlerte(int n);

  /// No description provided for @connexionAccroche.
  ///
  /// In fr, this message translates to:
  /// **'Le chantier dans la poche, même sans réseau.'**
  String get connexionAccroche;

  /// No description provided for @identifiant.
  ///
  /// In fr, this message translates to:
  /// **'Identifiant'**
  String get identifiant;

  /// No description provided for @motDePasse.
  ///
  /// In fr, this message translates to:
  /// **'Mot de passe'**
  String get motDePasse;

  /// No description provided for @afficherMotDePasse.
  ///
  /// In fr, this message translates to:
  /// **'Afficher le mot de passe'**
  String get afficherMotDePasse;

  /// No description provided for @masquerMotDePasse.
  ///
  /// In fr, this message translates to:
  /// **'Masquer le mot de passe'**
  String get masquerMotDePasse;

  /// No description provided for @connexionAide.
  ///
  /// In fr, this message translates to:
  /// **'Connexion en ligne requise une seule fois, puis accès par code PIN.'**
  String get connexionAide;

  /// No description provided for @comptesDemoTitre.
  ///
  /// In fr, this message translates to:
  /// **'Comptes de démonstration'**
  String get comptesDemoTitre;

  /// No description provided for @comptesDemoAide.
  ///
  /// In fr, this message translates to:
  /// **'Affichés uniquement parce que les données sont simulées. Touchez un profil pour remplir le formulaire.'**
  String get comptesDemoAide;

  /// No description provided for @erreurIdentifiants.
  ///
  /// In fr, this message translates to:
  /// **'Identifiant ou mot de passe incorrect.'**
  String get erreurIdentifiants;

  /// No description provided for @erreurCompteInactif.
  ///
  /// In fr, this message translates to:
  /// **'Ce compte est désactivé. Contactez votre administrateur.'**
  String get erreurCompteInactif;

  /// No description provided for @erreurVerrouille.
  ///
  /// In fr, this message translates to:
  /// **'{secondes, plural, =0{Compte temporairement verrouillé après plusieurs échecs.} =1{Compte verrouillé. Réessayez dans 1 seconde.} other{Compte verrouillé. Réessayez dans {secondes} secondes.}}'**
  String erreurVerrouille(int secondes);

  /// No description provided for @erreurSansAccesTerrain.
  ///
  /// In fr, this message translates to:
  /// **'Ce compte n\'a pas d\'accès terrain sur l\'application mobile.'**
  String get erreurSansAccesTerrain;

  /// No description provided for @infoSessionRevoquee.
  ///
  /// In fr, this message translates to:
  /// **'Le compte a été retiré de cet appareil.'**
  String get infoSessionRevoquee;

  /// No description provided for @infoSessionExpiree.
  ///
  /// In fr, this message translates to:
  /// **'Plus de 14 jours sans connexion en ligne : reconnectez-vous pour continuer.'**
  String get infoSessionExpiree;

  /// No description provided for @erreurDonneesInaccessibles.
  ///
  /// In fr, this message translates to:
  /// **'Impossible d\'ouvrir les données de l\'appareil.'**
  String get erreurDonneesInaccessibles;

  /// No description provided for @erreurConnexionImpossible.
  ///
  /// In fr, this message translates to:
  /// **'Connexion impossible. Vérifiez le réseau puis réessayez.'**
  String get erreurConnexionImpossible;

  /// No description provided for @definirCodeTitre.
  ///
  /// In fr, this message translates to:
  /// **'Définir mon code'**
  String get definirCodeTitre;

  /// No description provided for @definirCodeSousTitre.
  ///
  /// In fr, this message translates to:
  /// **'Pour ouvrir l\'application sans réseau'**
  String get definirCodeSousTitre;

  /// No description provided for @choisirCode.
  ///
  /// In fr, this message translates to:
  /// **'Choisissez un code'**
  String get choisirCode;

  /// No description provided for @choisirCodeAide.
  ///
  /// In fr, this message translates to:
  /// **'6 chiffres que vous serez seul à connaître.'**
  String get choisirCodeAide;

  /// No description provided for @confirmerCode.
  ///
  /// In fr, this message translates to:
  /// **'Confirmez le code'**
  String get confirmerCode;

  /// No description provided for @confirmerCodeAide.
  ///
  /// In fr, this message translates to:
  /// **'Saisissez à nouveau le même code.'**
  String get confirmerCodeAide;

  /// No description provided for @codesDifferents.
  ///
  /// In fr, this message translates to:
  /// **'Les deux codes ne correspondent pas. Recommencez.'**
  String get codesDifferents;

  /// No description provided for @synchroAJour.
  ///
  /// In fr, this message translates to:
  /// **'Données à jour'**
  String get synchroAJour;

  /// No description provided for @synchroEnAttente.
  ///
  /// In fr, this message translates to:
  /// **'{n, plural, =1{1 élément en attente d\'envoi} other{{n} éléments en attente d\'envoi}}'**
  String synchroEnAttente(int n);

  /// No description provided for @synchroTitre.
  ///
  /// In fr, this message translates to:
  /// **'Synchronisation'**
  String get synchroTitre;

  /// No description provided for @synchroExplication.
  ///
  /// In fr, this message translates to:
  /// **'Vos saisies sont enregistrées sur l\'appareil et partent dès que la connexion revient.'**
  String get synchroExplication;

  /// No description provided for @fileAttenteTitre.
  ///
  /// In fr, this message translates to:
  /// **'File d\'attente'**
  String get fileAttenteTitre;

  /// No description provided for @fileVideTitre.
  ///
  /// In fr, this message translates to:
  /// **'Rien à envoyer'**
  String get fileVideTitre;

  /// No description provided for @fileVideTexte.
  ///
  /// In fr, this message translates to:
  /// **'Les saisies faites sans réseau apparaîtront ici en attendant leur envoi.'**
  String get fileVideTexte;

  /// No description provided for @etatEnAttenteEnvoi.
  ///
  /// In fr, this message translates to:
  /// **'En attente'**
  String get etatEnAttenteEnvoi;

  /// No description provided for @etatEnvoye.
  ///
  /// In fr, this message translates to:
  /// **'Envoyé'**
  String get etatEnvoye;

  /// No description provided for @signatureTitre.
  ///
  /// In fr, this message translates to:
  /// **'Signature par code PIN'**
  String get signatureTitre;

  /// No description provided for @signatureAide.
  ///
  /// In fr, this message translates to:
  /// **'Votre code confirme la décision.'**
  String get signatureAide;

  /// No description provided for @moduleEnPreparation.
  ///
  /// In fr, this message translates to:
  /// **'Cet espace est en cours d\'installation.'**
  String get moduleEnPreparation;

  /// No description provided for @profilLangue.
  ///
  /// In fr, this message translates to:
  /// **'Langue'**
  String get profilLangue;

  /// No description provided for @profilTheme.
  ///
  /// In fr, this message translates to:
  /// **'Apparence'**
  String get profilTheme;

  /// No description provided for @themeSysteme.
  ///
  /// In fr, this message translates to:
  /// **'Automatique'**
  String get themeSysteme;

  /// No description provided for @themeClair.
  ///
  /// In fr, this message translates to:
  /// **'Clair'**
  String get themeClair;

  /// No description provided for @themeSombre.
  ///
  /// In fr, this message translates to:
  /// **'Sombre'**
  String get themeSombre;

  /// No description provided for @profilSynchroAide.
  ///
  /// In fr, this message translates to:
  /// **'File d\'attente et état des envois'**
  String get profilSynchroAide;

  /// No description provided for @profilVerrouiller.
  ///
  /// In fr, this message translates to:
  /// **'Verrouiller'**
  String get profilVerrouiller;

  /// No description provided for @profilVerrouillerAide.
  ///
  /// In fr, this message translates to:
  /// **'Revenir à l\'écran du code PIN'**
  String get profilVerrouillerAide;

  /// No description provided for @profilRetirerAide.
  ///
  /// In fr, this message translates to:
  /// **'Efface les données de cet appareil'**
  String get profilRetirerAide;

  /// No description provided for @profilAPropos.
  ///
  /// In fr, this message translates to:
  /// **'Schiavone Group · Italia Construction\nAppareil {appareil} · version 1.0'**
  String profilAPropos(String appareil);
}

class _TraductionsDelegate extends LocalizationsDelegate<Traductions> {
  const _TraductionsDelegate();

  @override
  Future<Traductions> load(Locale locale) {
    return SynchronousFuture<Traductions>(lookupTraductions(locale));
  }

  @override
  bool isSupported(Locale locale) =>
      <String>['en', 'fr', 'it'].contains(locale.languageCode);

  @override
  bool shouldReload(_TraductionsDelegate old) => false;
}

Traductions lookupTraductions(Locale locale) {
  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'en':
      return TraductionsEn();
    case 'fr':
      return TraductionsFr();
    case 'it':
      return TraductionsIt();
  }

  throw FlutterError(
    'Traductions.delegate failed to load unsupported locale "$locale". This is likely '
    'an issue with the localizations generation tool. Please file an issue '
    'on GitHub with a reproducible sample app and the gen-l10n configuration '
    'that was used.',
  );
}
