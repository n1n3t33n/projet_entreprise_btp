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

  /// No description provided for @niveauVide.
  ///
  /// In fr, this message translates to:
  /// **'Vide'**
  String get niveauVide;

  /// No description provided for @niveauCritique.
  ///
  /// In fr, this message translates to:
  /// **'Critique'**
  String get niveauCritique;

  /// No description provided for @niveauMini.
  ///
  /// In fr, this message translates to:
  /// **'Mini'**
  String get niveauMini;

  /// No description provided for @niveauPlein.
  ///
  /// In fr, this message translates to:
  /// **'Plein'**
  String get niveauPlein;

  /// No description provided for @stockNegatif.
  ///
  /// In fr, this message translates to:
  /// **'Stock négatif'**
  String get stockNegatif;

  /// No description provided for @stockNegatifExplication.
  ///
  /// In fr, this message translates to:
  /// **'Le stock est négatif : anomalie à corriger par un inventaire.'**
  String get stockNegatifExplication;

  /// No description provided for @jaugeCapacite.
  ///
  /// In fr, this message translates to:
  /// **'Capacité'**
  String get jaugeCapacite;

  /// No description provided for @typeReception.
  ///
  /// In fr, this message translates to:
  /// **'Réception'**
  String get typeReception;

  /// No description provided for @typeSortie.
  ///
  /// In fr, this message translates to:
  /// **'Sortie'**
  String get typeSortie;

  /// No description provided for @typeRetour.
  ///
  /// In fr, this message translates to:
  /// **'Retour'**
  String get typeRetour;

  /// No description provided for @typePerte.
  ///
  /// In fr, this message translates to:
  /// **'Perte ou casse'**
  String get typePerte;

  /// No description provided for @typeAjustement.
  ///
  /// In fr, this message translates to:
  /// **'Ajustement d\'inventaire'**
  String get typeAjustement;

  /// No description provided for @statutEnregistre.
  ///
  /// In fr, this message translates to:
  /// **'Enregistré'**
  String get statutEnregistre;

  /// No description provided for @statutAValider.
  ///
  /// In fr, this message translates to:
  /// **'À valider'**
  String get statutAValider;

  /// No description provided for @statutValide.
  ///
  /// In fr, this message translates to:
  /// **'Validé'**
  String get statutValide;

  /// No description provided for @statutRejete.
  ///
  /// In fr, this message translates to:
  /// **'Refusé'**
  String get statutRejete;

  /// No description provided for @aLInstant.
  ///
  /// In fr, this message translates to:
  /// **'à l\'instant'**
  String get aLInstant;

  /// No description provided for @ilYAMinutes.
  ///
  /// In fr, this message translates to:
  /// **'il y a {n} min'**
  String ilYAMinutes(int n);

  /// No description provided for @ilYAHeures.
  ///
  /// In fr, this message translates to:
  /// **'il y a {n} h'**
  String ilYAHeures(int n);

  /// No description provided for @aujourdhui.
  ///
  /// In fr, this message translates to:
  /// **'Aujourd\'hui'**
  String get aujourdhui;

  /// No description provided for @hier.
  ///
  /// In fr, this message translates to:
  /// **'Hier'**
  String get hier;

  /// No description provided for @choisirArticleTitre.
  ///
  /// In fr, this message translates to:
  /// **'Choisir un article'**
  String get choisirArticleTitre;

  /// No description provided for @rechercherArticle.
  ///
  /// In fr, this message translates to:
  /// **'Rechercher un article, un code…'**
  String get rechercherArticle;

  /// No description provided for @aucunResultat.
  ///
  /// In fr, this message translates to:
  /// **'Aucun article trouvé'**
  String get aucunResultat;

  /// No description provided for @aucunResultatAide.
  ///
  /// In fr, this message translates to:
  /// **'Modifiez la recherche ou le filtre.'**
  String get aucunResultatAide;

  /// No description provided for @stockActuel.
  ///
  /// In fr, this message translates to:
  /// **'stock actuel : {quantite}'**
  String stockActuel(String quantite);

  /// No description provided for @sortieTitre.
  ///
  /// In fr, this message translates to:
  /// **'Sortie rapide'**
  String get sortieTitre;

  /// No description provided for @sortieAide.
  ///
  /// In fr, this message translates to:
  /// **'Remettre du matériel à une équipe'**
  String get sortieAide;

  /// No description provided for @receptionTitre.
  ///
  /// In fr, this message translates to:
  /// **'Réception'**
  String get receptionTitre;

  /// No description provided for @receptionAide.
  ///
  /// In fr, this message translates to:
  /// **'Enregistrer un bon de livraison'**
  String get receptionAide;

  /// No description provided for @retourTitre.
  ///
  /// In fr, this message translates to:
  /// **'Retour, casse ou perte'**
  String get retourTitre;

  /// No description provided for @retourAide.
  ///
  /// In fr, this message translates to:
  /// **'Déclarer un surplus ou un matériel abîmé'**
  String get retourAide;

  /// No description provided for @retourCourt.
  ///
  /// In fr, this message translates to:
  /// **'Retour / perte'**
  String get retourCourt;

  /// No description provided for @saisieSousTitre.
  ///
  /// In fr, this message translates to:
  /// **'Enregistré sur l\'appareil'**
  String get saisieSousTitre;

  /// No description provided for @saisieArticle.
  ///
  /// In fr, this message translates to:
  /// **'Article'**
  String get saisieArticle;

  /// No description provided for @saisieQuantite.
  ///
  /// In fr, this message translates to:
  /// **'Quantité'**
  String get saisieQuantite;

  /// No description provided for @saisieMention.
  ///
  /// In fr, this message translates to:
  /// **'Envoi automatique au retour du réseau.'**
  String get saisieMention;

  /// No description provided for @saisieIncomplete.
  ///
  /// In fr, this message translates to:
  /// **'Complétez les champs obligatoires pour valider.'**
  String get saisieIncomplete;

  /// No description provided for @toutLeStock.
  ///
  /// In fr, this message translates to:
  /// **'Tout le stock ({quantite})'**
  String toutLeStock(String quantite);

  /// No description provided for @stockProjete.
  ///
  /// In fr, this message translates to:
  /// **'Stock après saisie'**
  String get stockProjete;

  /// No description provided for @sortieDestination.
  ///
  /// In fr, this message translates to:
  /// **'Destination'**
  String get sortieDestination;

  /// No description provided for @sortieLogement.
  ///
  /// In fr, this message translates to:
  /// **'Logement ou zone de pose'**
  String get sortieLogement;

  /// No description provided for @sortieCorpsEtat.
  ///
  /// In fr, this message translates to:
  /// **'Corps d\'état'**
  String get sortieCorpsEtat;

  /// No description provided for @sortieBeneficiaire.
  ///
  /// In fr, this message translates to:
  /// **'Équipe bénéficiaire'**
  String get sortieBeneficiaire;

  /// No description provided for @facultatif.
  ///
  /// In fr, this message translates to:
  /// **'Facultatif'**
  String get facultatif;

  /// No description provided for @receptionTracabilite.
  ///
  /// In fr, this message translates to:
  /// **'Bon de livraison et fournisseur'**
  String get receptionTracabilite;

  /// No description provided for @receptionBon.
  ///
  /// In fr, this message translates to:
  /// **'N° de bon de livraison ou de conteneur'**
  String get receptionBon;

  /// No description provided for @receptionBonExemple.
  ///
  /// In fr, this message translates to:
  /// **'Ex. BL-2026-0589'**
  String get receptionBonExemple;

  /// No description provided for @receptionFournisseur.
  ///
  /// In fr, this message translates to:
  /// **'Fournisseur'**
  String get receptionFournisseur;

  /// No description provided for @receptionEtat.
  ///
  /// In fr, this message translates to:
  /// **'État de la livraison'**
  String get receptionEtat;

  /// No description provided for @receptionConforme.
  ///
  /// In fr, this message translates to:
  /// **'Conforme'**
  String get receptionConforme;

  /// No description provided for @receptionReserves.
  ///
  /// In fr, this message translates to:
  /// **'Réserves'**
  String get receptionReserves;

  /// No description provided for @observations.
  ///
  /// In fr, this message translates to:
  /// **'Observations'**
  String get observations;

  /// No description provided for @receptionObservationsExemple.
  ///
  /// In fr, this message translates to:
  /// **'Ex. deux sacs éventrés au déchargement'**
  String get receptionObservationsExemple;

  /// No description provided for @retourNature.
  ///
  /// In fr, this message translates to:
  /// **'Nature de la déclaration'**
  String get retourNature;

  /// No description provided for @natureRetour.
  ///
  /// In fr, this message translates to:
  /// **'Retour au magasin'**
  String get natureRetour;

  /// No description provided for @natureRetourDetail.
  ///
  /// In fr, this message translates to:
  /// **'Surplus réintégré au stock'**
  String get natureRetourDetail;

  /// No description provided for @natureCasse.
  ///
  /// In fr, this message translates to:
  /// **'Casse ou avarie'**
  String get natureCasse;

  /// No description provided for @natureCasseDetail.
  ///
  /// In fr, this message translates to:
  /// **'Matériel abîmé, inutilisable'**
  String get natureCasseDetail;

  /// No description provided for @naturePerte.
  ///
  /// In fr, this message translates to:
  /// **'Perte'**
  String get naturePerte;

  /// No description provided for @naturePerteDetail.
  ///
  /// In fr, this message translates to:
  /// **'Matériel manquant, introuvable'**
  String get naturePerteDetail;

  /// No description provided for @retourMotif.
  ///
  /// In fr, this message translates to:
  /// **'Motif'**
  String get retourMotif;

  /// No description provided for @retourMotifAide.
  ///
  /// In fr, this message translates to:
  /// **'Choisir un motif'**
  String get retourMotifAide;

  /// No description provided for @retourObservationsExemple.
  ///
  /// In fr, this message translates to:
  /// **'Ex. palette restée sous la pluie'**
  String get retourObservationsExemple;

  /// No description provided for @motifSurplus.
  ///
  /// In fr, this message translates to:
  /// **'Surplus de chantier'**
  String get motifSurplus;

  /// No description provided for @motifErreurMetre.
  ///
  /// In fr, this message translates to:
  /// **'Erreur de métré'**
  String get motifErreurMetre;

  /// No description provided for @motifHumidite.
  ///
  /// In fr, this message translates to:
  /// **'Sac éventré ou humidité'**
  String get motifHumidite;

  /// No description provided for @motifChoc.
  ///
  /// In fr, this message translates to:
  /// **'Choc ou chute'**
  String get motifChoc;

  /// No description provided for @motifIntrouvable.
  ///
  /// In fr, this message translates to:
  /// **'Introuvable au comptage'**
  String get motifIntrouvable;

  /// No description provided for @motifAutre.
  ///
  /// In fr, this message translates to:
  /// **'Autre'**
  String get motifAutre;

  /// No description provided for @validerSortie.
  ///
  /// In fr, this message translates to:
  /// **'Valider la sortie ({quantite})'**
  String validerSortie(String quantite);

  /// No description provided for @enregistrerReception.
  ///
  /// In fr, this message translates to:
  /// **'Enregistrer la réception ({quantite})'**
  String enregistrerReception(String quantite);

  /// No description provided for @validerDeclaration.
  ///
  /// In fr, this message translates to:
  /// **'Valider la déclaration ({quantite})'**
  String validerDeclaration(String quantite);

  /// No description provided for @mouvementEnregistre.
  ///
  /// In fr, this message translates to:
  /// **'Mouvement enregistré sur l\'appareil.'**
  String get mouvementEnregistre;

  /// No description provided for @controleOk.
  ///
  /// In fr, this message translates to:
  /// **'Stock suffisant : la saisie laisse l\'article au-dessus de son seuil.'**
  String get controleOk;

  /// No description provided for @avertissementSeuil.
  ///
  /// In fr, this message translates to:
  /// **'Stock restant {reste}, sous le seuil mini de {seuil}.'**
  String avertissementSeuil(String reste, String seuil);

  /// No description provided for @avertissementNegatif.
  ///
  /// In fr, this message translates to:
  /// **'Cette saisie rend le stock négatif. Elle sera signalée comme anomalie.'**
  String get avertissementNegatif;

  /// No description provided for @registreTitre.
  ///
  /// In fr, this message translates to:
  /// **'Registre du stock'**
  String get registreTitre;

  /// No description provided for @registreSousTitre.
  ///
  /// In fr, this message translates to:
  /// **'Quantités connues de l\'appareil'**
  String get registreSousTitre;

  /// No description provided for @references.
  ///
  /// In fr, this message translates to:
  /// **'références'**
  String get references;

  /// No description provided for @nouveauMouvement.
  ///
  /// In fr, this message translates to:
  /// **'Nouveau mouvement'**
  String get nouveauMouvement;

  /// No description provided for @filtreTous.
  ///
  /// In fr, this message translates to:
  /// **'Tous'**
  String get filtreTous;

  /// No description provided for @filtreSousSeuil.
  ///
  /// In fr, this message translates to:
  /// **'Sous seuil'**
  String get filtreSousSeuil;

  /// No description provided for @filtreSorties.
  ///
  /// In fr, this message translates to:
  /// **'Sorties'**
  String get filtreSorties;

  /// No description provided for @filtreEntrees.
  ///
  /// In fr, this message translates to:
  /// **'Entrées'**
  String get filtreEntrees;

  /// No description provided for @seuilMini.
  ///
  /// In fr, this message translates to:
  /// **'Seuil mini : {seuil}'**
  String seuilMini(String seuil);

  /// No description provided for @seuilMiniEcart.
  ///
  /// In fr, this message translates to:
  /// **'Seuil mini : {seuil} ({ecart})'**
  String seuilMiniEcart(String seuil, String ecart);

  /// No description provided for @stockConforme.
  ///
  /// In fr, this message translates to:
  /// **'Stock conforme (mini : {seuil})'**
  String stockConforme(String seuil);

  /// No description provided for @ficheArticleTitre.
  ///
  /// In fr, this message translates to:
  /// **'Fiche article'**
  String get ficheArticleTitre;

  /// No description provided for @disponibles.
  ///
  /// In fr, this message translates to:
  /// **'{unite} en stock'**
  String disponibles(String unite);

  /// No description provided for @mouvementsRecents.
  ///
  /// In fr, this message translates to:
  /// **'Mouvements récents'**
  String get mouvementsRecents;

  /// No description provided for @journalComplet.
  ///
  /// In fr, this message translates to:
  /// **'Journal complet'**
  String get journalComplet;

  /// No description provided for @aucunMouvement.
  ///
  /// In fr, this message translates to:
  /// **'Aucun mouvement'**
  String get aucunMouvement;

  /// No description provided for @aucunMouvementAide.
  ///
  /// In fr, this message translates to:
  /// **'Les sorties, réceptions et retours apparaîtront ici.'**
  String get aucunMouvementAide;

  /// No description provided for @codeBarres.
  ///
  /// In fr, this message translates to:
  /// **'Code-barres'**
  String get codeBarres;

  /// No description provided for @journalTitre.
  ///
  /// In fr, this message translates to:
  /// **'Journal des mouvements'**
  String get journalTitre;

  /// No description provided for @journalSousTitre.
  ///
  /// In fr, this message translates to:
  /// **'Entrées et sorties du magasin'**
  String get journalSousTitre;

  /// No description provided for @journalRecherche.
  ///
  /// In fr, this message translates to:
  /// **'Rechercher un bon, un article, une personne…'**
  String get journalRecherche;

  /// No description provided for @mouvementsDuJour.
  ///
  /// In fr, this message translates to:
  /// **'mouvements du jour'**
  String get mouvementsDuJour;

  /// No description provided for @entreesDuJour.
  ///
  /// In fr, this message translates to:
  /// **'entrées du jour'**
  String get entreesDuJour;

  /// No description provided for @journalNonModifiable.
  ///
  /// In fr, this message translates to:
  /// **'Journal horodaté et non modifiable'**
  String get journalNonModifiable;

  /// No description provided for @validationTitre.
  ///
  /// In fr, this message translates to:
  /// **'Validations'**
  String get validationTitre;

  /// No description provided for @validationSousTitre.
  ///
  /// In fr, this message translates to:
  /// **'Sorties de stock et alertes'**
  String get validationSousTitre;

  /// No description provided for @ongletDemandes.
  ///
  /// In fr, this message translates to:
  /// **'Demandes'**
  String get ongletDemandes;

  /// No description provided for @ongletAlertes.
  ///
  /// In fr, this message translates to:
  /// **'Alertes de seuil'**
  String get ongletAlertes;

  /// No description provided for @aucuneDemande.
  ///
  /// In fr, this message translates to:
  /// **'Aucune sortie à valider'**
  String get aucuneDemande;

  /// No description provided for @aucuneDemandeAide.
  ///
  /// In fr, this message translates to:
  /// **'Les sorties saisies par les magasiniers apparaîtront ici.'**
  String get aucuneDemandeAide;

  /// No description provided for @aucuneAlerte.
  ///
  /// In fr, this message translates to:
  /// **'Aucune alerte'**
  String get aucuneAlerte;

  /// No description provided for @aucuneAlerteAide.
  ///
  /// In fr, this message translates to:
  /// **'Tous les articles sont au-dessus de leur seuil.'**
  String get aucuneAlerteAide;

  /// No description provided for @materiau.
  ///
  /// In fr, this message translates to:
  /// **'Matériau'**
  String get materiau;

  /// No description provided for @demandeur.
  ///
  /// In fr, this message translates to:
  /// **'Saisi par'**
  String get demandeur;

  /// No description provided for @affectation.
  ///
  /// In fr, this message translates to:
  /// **'Destination'**
  String get affectation;

  /// No description provided for @rejeter.
  ///
  /// In fr, this message translates to:
  /// **'Refuser'**
  String get rejeter;

  /// No description provided for @approuver.
  ///
  /// In fr, this message translates to:
  /// **'Approuver'**
  String get approuver;

  /// No description provided for @signatureSortie.
  ///
  /// In fr, this message translates to:
  /// **'Approuver la sortie {numero} ({quantite}).'**
  String signatureSortie(String numero, String quantite);

  /// No description provided for @sortieApprouvee.
  ///
  /// In fr, this message translates to:
  /// **'Sortie approuvée.'**
  String get sortieApprouvee;

  /// No description provided for @sortieRefusee.
  ///
  /// In fr, this message translates to:
  /// **'Sortie refusée : la quantité revient en stock.'**
  String get sortieRefusee;

  /// No description provided for @separationFonctions.
  ///
  /// In fr, this message translates to:
  /// **'Vous avez saisi cette opération : une autre personne doit la valider.'**
  String get separationFonctions;

  /// No description provided for @stockRestant.
  ///
  /// In fr, this message translates to:
  /// **'Stock restant :'**
  String get stockRestant;

  /// No description provided for @inventaireTitre.
  ///
  /// In fr, this message translates to:
  /// **'Inventaire tournant'**
  String get inventaireTitre;

  /// No description provided for @inventaireEnCours.
  ///
  /// In fr, this message translates to:
  /// **'En cours'**
  String get inventaireEnCours;

  /// No description provided for @inventaireProgression.
  ///
  /// In fr, this message translates to:
  /// **'{faits, plural, =1{1 article compté} other{{faits} articles comptés}} sur {total}'**
  String inventaireProgression(int faits, int total);

  /// No description provided for @articleEnControle.
  ///
  /// In fr, this message translates to:
  /// **'Article à compter'**
  String get articleEnControle;

  /// No description provided for @stockTheorique.
  ///
  /// In fr, this message translates to:
  /// **'Stock attendu'**
  String get stockTheorique;

  /// No description provided for @quantiteComptee.
  ///
  /// In fr, this message translates to:
  /// **'Quantité comptée'**
  String get quantiteComptee;

  /// No description provided for @ecartDetecte.
  ///
  /// In fr, this message translates to:
  /// **'Écart constaté : {ecart}. Justification obligatoire.'**
  String ecartDetecte(String ecart);

  /// No description provided for @ecartChutes.
  ///
  /// In fr, this message translates to:
  /// **'Chutes de coupe'**
  String get ecartChutes;

  /// No description provided for @ecartRebut.
  ///
  /// In fr, this message translates to:
  /// **'Matériel au rebut'**
  String get ecartRebut;

  /// No description provided for @ecartNonDeclare.
  ///
  /// In fr, this message translates to:
  /// **'Mouvement non déclaré'**
  String get ecartNonDeclare;

  /// No description provided for @ecartRecompter.
  ///
  /// In fr, this message translates to:
  /// **'Comptage à refaire'**
  String get ecartRecompter;

  /// No description provided for @justificationObligatoire.
  ///
  /// In fr, this message translates to:
  /// **'Choisissez une justification pour l\'écart.'**
  String get justificationObligatoire;

  /// No description provided for @validerArticle.
  ///
  /// In fr, this message translates to:
  /// **'Valider {quantite} et passer au suivant'**
  String validerArticle(String quantite);

  /// No description provided for @soumettreInventaire.
  ///
  /// In fr, this message translates to:
  /// **'Soumettre l\'inventaire à validation'**
  String get soumettreInventaire;

  /// No description provided for @inventaireSoumis.
  ///
  /// In fr, this message translates to:
  /// **'Inventaire transmis pour validation.'**
  String get inventaireSoumis;

  /// No description provided for @validerInventaire.
  ///
  /// In fr, this message translates to:
  /// **'Valider l\'inventaire'**
  String get validerInventaire;

  /// No description provided for @inventaireValide.
  ///
  /// In fr, this message translates to:
  /// **'Inventaire validé : le stock a été ajusté.'**
  String get inventaireValide;

  /// No description provided for @inventaireRegle.
  ///
  /// In fr, this message translates to:
  /// **'Le stock n\'est ajusté qu\'après cette validation.'**
  String get inventaireRegle;

  /// No description provided for @signatureInventaire.
  ///
  /// In fr, this message translates to:
  /// **'Valider l\'inventaire {id} et ajuster le stock ({n} écarts).'**
  String signatureInventaire(String id, int n);

  /// No description provided for @inventaireEnAttenteValidation.
  ///
  /// In fr, this message translates to:
  /// **'Comptage terminé. L\'inventaire attend la validation du gestionnaire de stock.'**
  String get inventaireEnAttenteValidation;

  /// No description provided for @inventaireArticles.
  ///
  /// In fr, this message translates to:
  /// **'Articles de la zone'**
  String get inventaireArticles;

  /// No description provided for @inventaireAValider.
  ///
  /// In fr, this message translates to:
  /// **'Inventaire à valider'**
  String get inventaireAValider;

  /// No description provided for @inventaireEcarts.
  ///
  /// In fr, this message translates to:
  /// **'{n, plural, =0{Aucun écart} =1{1 écart à examiner} other{{n} écarts à examiner}}'**
  String inventaireEcarts(int n);

  /// No description provided for @aCompter.
  ///
  /// In fr, this message translates to:
  /// **'À compter'**
  String get aCompter;

  /// No description provided for @conforme.
  ///
  /// In fr, this message translates to:
  /// **'Conforme'**
  String get conforme;

  /// No description provided for @alertesPriorites.
  ///
  /// In fr, this message translates to:
  /// **'Alertes et priorités'**
  String get alertesPriorites;

  /// No description provided for @voirToutesAlertes.
  ///
  /// In fr, this message translates to:
  /// **'Voir les {n} alertes'**
  String voirToutesAlertes(int n);

  /// No description provided for @stockMagasin.
  ///
  /// In fr, this message translates to:
  /// **'Stock du magasin'**
  String get stockMagasin;

  /// No description provided for @sousSeuil.
  ///
  /// In fr, this message translates to:
  /// **'sous seuil'**
  String get sousSeuil;

  /// No description provided for @consulterStock.
  ///
  /// In fr, this message translates to:
  /// **'Consulter le stock'**
  String get consulterStock;

  /// No description provided for @consulterRegistre.
  ///
  /// In fr, this message translates to:
  /// **'Consulter le registre'**
  String get consulterRegistre;

  /// No description provided for @raccourcis.
  ///
  /// In fr, this message translates to:
  /// **'Raccourcis'**
  String get raccourcis;

  /// No description provided for @reprendreComptage.
  ///
  /// In fr, this message translates to:
  /// **'Reprendre le comptage'**
  String get reprendreComptage;

  /// No description provided for @suivreInventaire.
  ///
  /// In fr, this message translates to:
  /// **'Suivre le comptage'**
  String get suivreInventaire;

  /// No description provided for @mouvements24h.
  ///
  /// In fr, this message translates to:
  /// **'mouv. sur 24 h'**
  String get mouvements24h;

  /// No description provided for @sortiesAValider.
  ///
  /// In fr, this message translates to:
  /// **'Sorties à valider'**
  String get sortiesAValider;

  /// No description provided for @nombreDemandes.
  ///
  /// In fr, this message translates to:
  /// **'{n, plural, =0{À jour} =1{1 demande} other{{n} demandes}}'**
  String nombreDemandes(int n);

  /// No description provided for @examinerSorties.
  ///
  /// In fr, this message translates to:
  /// **'Examiner les {n} sorties'**
  String examinerSorties(int n);

  /// No description provided for @etapeAFaire.
  ///
  /// In fr, this message translates to:
  /// **'À faire'**
  String get etapeAFaire;

  /// No description provided for @etapeEnCours.
  ///
  /// In fr, this message translates to:
  /// **'En cours'**
  String get etapeEnCours;

  /// No description provided for @etapeADeclaree.
  ///
  /// In fr, this message translates to:
  /// **'À valider'**
  String get etapeADeclaree;

  /// No description provided for @etapeValidee.
  ///
  /// In fr, this message translates to:
  /// **'Validée'**
  String get etapeValidee;

  /// No description provided for @etapeBloquee.
  ///
  /// In fr, this message translates to:
  /// **'Bloquée'**
  String get etapeBloquee;

  /// No description provided for @etapesFaites.
  ///
  /// In fr, this message translates to:
  /// **'terminées'**
  String get etapesFaites;

  /// No description provided for @filtreToutes.
  ///
  /// In fr, this message translates to:
  /// **'Toutes'**
  String get filtreToutes;

  /// No description provided for @evDemarrage.
  ///
  /// In fr, this message translates to:
  /// **'Démarrage'**
  String get evDemarrage;

  /// No description provided for @evPointage.
  ///
  /// In fr, this message translates to:
  /// **'Pointage'**
  String get evPointage;

  /// No description provided for @evPause.
  ///
  /// In fr, this message translates to:
  /// **'Pause'**
  String get evPause;

  /// No description provided for @evReprise.
  ///
  /// In fr, this message translates to:
  /// **'Reprise'**
  String get evReprise;

  /// No description provided for @evBlocage.
  ///
  /// In fr, this message translates to:
  /// **'Blocage'**
  String get evBlocage;

  /// No description provided for @evLeveeBlocage.
  ///
  /// In fr, this message translates to:
  /// **'Blocage levé'**
  String get evLeveeBlocage;

  /// No description provided for @evFin.
  ///
  /// In fr, this message translates to:
  /// **'Fin déclarée'**
  String get evFin;

  /// No description provided for @evValidation.
  ///
  /// In fr, this message translates to:
  /// **'Validation'**
  String get evValidation;

  /// No description provided for @evRejet.
  ///
  /// In fr, this message translates to:
  /// **'Reprise demandée'**
  String get evRejet;

  /// No description provided for @evReaffectation.
  ///
  /// In fr, this message translates to:
  /// **'Réaffectation'**
  String get evReaffectation;

  /// No description provided for @blocageRupture.
  ///
  /// In fr, this message translates to:
  /// **'Rupture de matériau'**
  String get blocageRupture;

  /// No description provided for @blocagePanne.
  ///
  /// In fr, this message translates to:
  /// **'Panne d\'engin ou d\'outillage'**
  String get blocagePanne;

  /// No description provided for @blocageIntemperies.
  ///
  /// In fr, this message translates to:
  /// **'Intempéries'**
  String get blocageIntemperies;

  /// No description provided for @blocageNonConformite.
  ///
  /// In fr, this message translates to:
  /// **'Non-conformité du support'**
  String get blocageNonConformite;

  /// No description provided for @blocageAcces.
  ///
  /// In fr, this message translates to:
  /// **'Accès au chantier bloqué'**
  String get blocageAcces;

  /// No description provided for @graviteArret.
  ///
  /// In fr, this message translates to:
  /// **'Arrêt total'**
  String get graviteArret;

  /// No description provided for @graviteRalenti.
  ///
  /// In fr, this message translates to:
  /// **'Ralenti'**
  String get graviteRalenti;

  /// No description provided for @graviteAlerte.
  ///
  /// In fr, this message translates to:
  /// **'Simple alerte'**
  String get graviteAlerte;

  /// No description provided for @retardDeuxHeures.
  ///
  /// In fr, this message translates to:
  /// **'2 heures'**
  String get retardDeuxHeures;

  /// No description provided for @retardDemiJournee.
  ///
  /// In fr, this message translates to:
  /// **'Demi-journée'**
  String get retardDemiJournee;

  /// No description provided for @retardUnJour.
  ///
  /// In fr, this message translates to:
  /// **'Un jour ou plus'**
  String get retardUnJour;

  /// No description provided for @ficheRouteTitre.
  ///
  /// In fr, this message translates to:
  /// **'Fiche de route'**
  String get ficheRouteTitre;

  /// No description provided for @progressionJour.
  ///
  /// In fr, this message translates to:
  /// **'Progression du jour'**
  String get progressionJour;

  /// No description provided for @etapesTerminees.
  ///
  /// In fr, this message translates to:
  /// **'{faits} étapes terminées sur {total}'**
  String etapesTerminees(int faits, int total);

  /// No description provided for @aucuneEtape.
  ///
  /// In fr, this message translates to:
  /// **'Aucune étape'**
  String get aucuneEtape;

  /// No description provided for @aucuneEtapeAide.
  ///
  /// In fr, this message translates to:
  /// **'Aucune étape ne correspond pour le moment.'**
  String get aucuneEtapeAide;

  /// No description provided for @etapeTitre.
  ///
  /// In fr, this message translates to:
  /// **'Étape {id}'**
  String etapeTitre(String id);

  /// No description provided for @actionImpossible.
  ///
  /// In fr, this message translates to:
  /// **'Action impossible dans l\'état actuel de l\'étape.'**
  String get actionImpossible;

  /// No description provided for @demarrerEtape.
  ///
  /// In fr, this message translates to:
  /// **'Démarrer l\'étape'**
  String get demarrerEtape;

  /// No description provided for @validerPointage.
  ///
  /// In fr, this message translates to:
  /// **'Enregistrer le pointage ({valeur})'**
  String validerPointage(String valeur);

  /// No description provided for @pointageEnregistre.
  ///
  /// In fr, this message translates to:
  /// **'Pointage enregistré sur l\'appareil.'**
  String get pointageEnregistre;

  /// No description provided for @terminerEtape.
  ///
  /// In fr, this message translates to:
  /// **'Déclarer l\'étape terminée'**
  String get terminerEtape;

  /// No description provided for @etapeDeclaree.
  ///
  /// In fr, this message translates to:
  /// **'Étape déclarée terminée : elle attend sa validation.'**
  String get etapeDeclaree;

  /// No description provided for @terminerMention.
  ///
  /// In fr, this message translates to:
  /// **'Une autre personne devra valider l\'étape.'**
  String get terminerMention;

  /// No description provided for @terminerConditions.
  ///
  /// In fr, this message translates to:
  /// **'Pour terminer : métré atteint et tous les contrôles cochés.'**
  String get terminerConditions;

  /// No description provided for @leverBlocage.
  ///
  /// In fr, this message translates to:
  /// **'Lever le blocage'**
  String get leverBlocage;

  /// No description provided for @journalEtapeTitre.
  ///
  /// In fr, this message translates to:
  /// **'Journal d\'étape'**
  String get journalEtapeTitre;

  /// No description provided for @journalEtapeSousTitre.
  ///
  /// In fr, this message translates to:
  /// **'Activité horodatée'**
  String get journalEtapeSousTitre;

  /// No description provided for @localisation.
  ///
  /// In fr, this message translates to:
  /// **'Localisation'**
  String get localisation;

  /// No description provided for @pointageActif.
  ///
  /// In fr, this message translates to:
  /// **'POINTAGE EN COURS'**
  String get pointageActif;

  /// No description provided for @pointageArrete.
  ///
  /// In fr, this message translates to:
  /// **'POINTAGE EN PAUSE'**
  String get pointageArrete;

  /// No description provided for @mettreEnPause.
  ///
  /// In fr, this message translates to:
  /// **'Mettre en pause'**
  String get mettreEnPause;

  /// No description provided for @reprendre.
  ///
  /// In fr, this message translates to:
  /// **'Reprendre'**
  String get reprendre;

  /// No description provided for @avancementMetre.
  ///
  /// In fr, this message translates to:
  /// **'Avancement du métré'**
  String get avancementMetre;

  /// No description provided for @cible.
  ///
  /// In fr, this message translates to:
  /// **'Cible : {valeur}'**
  String cible(String valeur);

  /// No description provided for @surCible.
  ///
  /// In fr, this message translates to:
  /// **'sur {valeur}'**
  String surCible(String valeur);

  /// No description provided for @solde.
  ///
  /// In fr, this message translates to:
  /// **'Solde total'**
  String get solde;

  /// No description provided for @gammeSecurite.
  ///
  /// In fr, this message translates to:
  /// **'Gamme opératoire et sécurité'**
  String get gammeSecurite;

  /// No description provided for @declarerBlocage.
  ///
  /// In fr, this message translates to:
  /// **'Déclarer un blocage'**
  String get declarerBlocage;

  /// No description provided for @reaffecterEtape.
  ///
  /// In fr, this message translates to:
  /// **'Réaffecter à une autre équipe'**
  String get reaffecterEtape;

  /// No description provided for @blocageTitre.
  ///
  /// In fr, this message translates to:
  /// **'Déclarer un blocage'**
  String get blocageTitre;

  /// No description provided for @blocageMention.
  ///
  /// In fr, this message translates to:
  /// **'L\'alerte part vers le bureau dès que la connexion revient.'**
  String get blocageMention;

  /// No description provided for @transmettreBlocage.
  ///
  /// In fr, this message translates to:
  /// **'Transmettre l\'alerte de blocage'**
  String get transmettreBlocage;

  /// No description provided for @blocageTransmis.
  ///
  /// In fr, this message translates to:
  /// **'Blocage enregistré : l\'étape est arrêtée.'**
  String get blocageTransmis;

  /// No description provided for @blocageNature.
  ///
  /// In fr, this message translates to:
  /// **'Nature du blocage'**
  String get blocageNature;

  /// No description provided for @blocageArticle.
  ///
  /// In fr, this message translates to:
  /// **'Désigner l\'article manquant'**
  String get blocageArticle;

  /// No description provided for @blocageGravite.
  ///
  /// In fr, this message translates to:
  /// **'Gravité'**
  String get blocageGravite;

  /// No description provided for @blocageRetard.
  ///
  /// In fr, this message translates to:
  /// **'Retard estimé'**
  String get blocageRetard;

  /// No description provided for @blocageObservationsExemple.
  ///
  /// In fr, this message translates to:
  /// **'Ex. livraison de ciment retardée de 3 h'**
  String get blocageObservationsExemple;

  /// No description provided for @controlesTitre.
  ///
  /// In fr, this message translates to:
  /// **'Contrôles et réception'**
  String get controlesTitre;

  /// No description provided for @controlesSousTitre.
  ///
  /// In fr, this message translates to:
  /// **'Étapes déclarées terminées'**
  String get controlesSousTitre;

  /// No description provided for @signatureEtape.
  ///
  /// In fr, this message translates to:
  /// **'Valider l\'étape {id} : {libelle}.'**
  String signatureEtape(String id, String libelle);

  /// No description provided for @etapeValideeMessage.
  ///
  /// In fr, this message translates to:
  /// **'Étape validée.'**
  String get etapeValideeMessage;

  /// No description provided for @etapeRefuseeMessage.
  ///
  /// In fr, this message translates to:
  /// **'Reprise demandée : l\'étape repasse en cours.'**
  String get etapeRefuseeMessage;

  /// No description provided for @aucunControle.
  ///
  /// In fr, this message translates to:
  /// **'Aucune étape à valider'**
  String get aucunControle;

  /// No description provided for @aucunControleAide.
  ///
  /// In fr, this message translates to:
  /// **'Les étapes déclarées terminées apparaîtront ici.'**
  String get aucunControleAide;

  /// No description provided for @declarePar.
  ///
  /// In fr, this message translates to:
  /// **'Déclarée terminée par {nom}'**
  String declarePar(String nom);

  /// No description provided for @validerEtape.
  ///
  /// In fr, this message translates to:
  /// **'Valider'**
  String get validerEtape;

  /// No description provided for @reaffectationTitre.
  ///
  /// In fr, this message translates to:
  /// **'Réaffectation'**
  String get reaffectationTitre;

  /// No description provided for @reaffectationMention.
  ///
  /// In fr, this message translates to:
  /// **'La nouvelle équipe verra l\'étape sur sa fiche de route.'**
  String get reaffectationMention;

  /// No description provided for @confirmerReaffectation.
  ///
  /// In fr, this message translates to:
  /// **'Confirmer la réaffectation'**
  String get confirmerReaffectation;

  /// No description provided for @reaffectationFaite.
  ///
  /// In fr, this message translates to:
  /// **'Étape confiée à {equipe}.'**
  String reaffectationFaite(String equipe);

  /// No description provided for @reaffectationMotif.
  ///
  /// In fr, this message translates to:
  /// **'Motif'**
  String get reaffectationMotif;

  /// No description provided for @motifRetardPlanning.
  ///
  /// In fr, this message translates to:
  /// **'Retard de planning'**
  String get motifRetardPlanning;

  /// No description provided for @motifAbsence.
  ///
  /// In fr, this message translates to:
  /// **'Absence d\'ouvriers'**
  String get motifAbsence;

  /// No description provided for @motifCompetence.
  ///
  /// In fr, this message translates to:
  /// **'Compétence requise'**
  String get motifCompetence;

  /// No description provided for @motifSurcroit.
  ///
  /// In fr, this message translates to:
  /// **'Surcroît d\'activité'**
  String get motifSurcroit;

  /// No description provided for @reaffectationEquipe.
  ///
  /// In fr, this message translates to:
  /// **'Nouvelle équipe'**
  String get reaffectationEquipe;

  /// No description provided for @equipeDetail.
  ///
  /// In fr, this message translates to:
  /// **'Chef : {chef} · {n} ouvriers'**
  String equipeDetail(String chef, int n);

  /// No description provided for @chargeActuelle.
  ///
  /// In fr, this message translates to:
  /// **'Charge'**
  String get chargeActuelle;

  /// No description provided for @reaffectationConsigne.
  ///
  /// In fr, this message translates to:
  /// **'Consigne de transmission'**
  String get reaffectationConsigne;

  /// No description provided for @reaffectationConsigneExemple.
  ///
  /// In fr, this message translates to:
  /// **'Ex. coffrage prêt, attendre la livraison du béton'**
  String get reaffectationConsigneExemple;

  /// No description provided for @dureePointee.
  ///
  /// In fr, this message translates to:
  /// **'temps pointé'**
  String get dureePointee;

  /// No description provided for @evenementsTraces.
  ///
  /// In fr, this message translates to:
  /// **'événements tracés'**
  String get evenementsTraces;

  /// No description provided for @aucunEvenement.
  ///
  /// In fr, this message translates to:
  /// **'Aucune activité'**
  String get aucunEvenement;

  /// No description provided for @aucunEvenementAide.
  ///
  /// In fr, this message translates to:
  /// **'Les démarrages, pointages et validations apparaîtront ici.'**
  String get aucunEvenementAide;

  /// No description provided for @pourcentRealise.
  ///
  /// In fr, this message translates to:
  /// **'{n} % réalisé'**
  String pourcentRealise(int n);

  /// No description provided for @ouvrirFicheRoute.
  ///
  /// In fr, this message translates to:
  /// **'Ouvrir la fiche de route'**
  String get ouvrirFicheRoute;

  /// No description provided for @maFicheDuJour.
  ///
  /// In fr, this message translates to:
  /// **'Ma fiche de route du jour'**
  String get maFicheDuJour;

  /// No description provided for @pointageRapide.
  ///
  /// In fr, this message translates to:
  /// **'Pointage rapide'**
  String get pointageRapide;

  /// No description provided for @prochainesEtapes.
  ///
  /// In fr, this message translates to:
  /// **'Prochaines étapes'**
  String get prochainesEtapes;

  /// No description provided for @aValiderPriorite.
  ///
  /// In fr, this message translates to:
  /// **'À valider en priorité'**
  String get aValiderPriorite;

  /// No description provided for @nombreActions.
  ///
  /// In fr, this message translates to:
  /// **'{n, plural, =0{À jour} =1{1 action} other{{n} actions}}'**
  String nombreActions(int n);

  /// No description provided for @sortiesAValiderDetail.
  ///
  /// In fr, this message translates to:
  /// **'Bons de matériel du magasin'**
  String get sortiesAValiderDetail;

  /// No description provided for @etapesAControler.
  ///
  /// In fr, this message translates to:
  /// **'Étapes à contrôler'**
  String get etapesAControler;

  /// No description provided for @etapesAControlerDetail.
  ///
  /// In fr, this message translates to:
  /// **'Travaux déclarés terminés'**
  String get etapesAControlerDetail;

  /// No description provided for @nombreEtapes.
  ///
  /// In fr, this message translates to:
  /// **'{n, plural, =0{Aucune étape} =1{1 étape} other{{n} étapes}}'**
  String nombreEtapes(int n);

  /// No description provided for @blocagesPrioritaires.
  ///
  /// In fr, this message translates to:
  /// **'Blocages en cours'**
  String get blocagesPrioritaires;

  /// No description provided for @aucunBlocage.
  ///
  /// In fr, this message translates to:
  /// **'Aucune étape bloquée.'**
  String get aucunBlocage;

  /// No description provided for @supervisionTravaux.
  ///
  /// In fr, this message translates to:
  /// **'Supervision des travaux et conformité'**
  String get supervisionTravaux;

  /// No description provided for @visasTechniques.
  ///
  /// In fr, this message translates to:
  /// **'Visas techniques'**
  String get visasTechniques;

  /// No description provided for @examinerEtapes.
  ///
  /// In fr, this message translates to:
  /// **'Examiner les étapes'**
  String get examinerEtapes;

  /// No description provided for @syntheseChantier.
  ///
  /// In fr, this message translates to:
  /// **'Synthèse par corps d\'état'**
  String get syntheseChantier;

  /// No description provided for @etapesValideesSur.
  ///
  /// In fr, this message translates to:
  /// **'{faits} étapes validées sur {total}'**
  String etapesValideesSur(int faits, int total);

  /// No description provided for @outilsPosteFixe.
  ///
  /// In fr, this message translates to:
  /// **'Outils complets sur poste fixe'**
  String get outilsPosteFixe;

  /// No description provided for @outilsPosteFixeAide.
  ///
  /// In fr, this message translates to:
  /// **'Plannings, équipes et exports se pilotent depuis le poste de pilotage web.'**
  String get outilsPosteFixeAide;

  /// No description provided for @synchroTerminee.
  ///
  /// In fr, this message translates to:
  /// **'{n, plural, =0{Rien à envoyer.} =1{1 élément envoyé.} other{{n} éléments envoyés.}}'**
  String synchroTerminee(int n);

  /// No description provided for @derniereSynchro.
  ///
  /// In fr, this message translates to:
  /// **'Dernière synchronisation'**
  String get derniereSynchro;

  /// No description provided for @jamais.
  ///
  /// In fr, this message translates to:
  /// **'Jamais'**
  String get jamais;

  /// No description provided for @synchroniserMaintenant.
  ///
  /// In fr, this message translates to:
  /// **'Synchroniser maintenant'**
  String get synchroniserMaintenant;

  /// No description provided for @conflitsTitre.
  ///
  /// In fr, this message translates to:
  /// **'Écarts à arbitrer'**
  String get conflitsTitre;

  /// No description provided for @conflitExplication.
  ///
  /// In fr, this message translates to:
  /// **'La quantité saisie sur l\'appareil dépasse ce que le serveur connaît.'**
  String get conflitExplication;

  /// No description provided for @cetAppareil.
  ///
  /// In fr, this message translates to:
  /// **'Sortie saisie ici'**
  String get cetAppareil;

  /// No description provided for @serveur.
  ///
  /// In fr, this message translates to:
  /// **'Stock connu du bureau'**
  String get serveur;

  /// No description provided for @resolutionServeur.
  ///
  /// In fr, this message translates to:
  /// **'Suivre le bureau (recommandé)'**
  String get resolutionServeur;

  /// No description provided for @resolutionServeurDetail.
  ///
  /// In fr, this message translates to:
  /// **'La sortie est ramenée à la quantité disponible.'**
  String get resolutionServeurDetail;

  /// No description provided for @resolutionLocale.
  ///
  /// In fr, this message translates to:
  /// **'Garder la saisie du terrain'**
  String get resolutionLocale;

  /// No description provided for @resolutionLocaleDetail.
  ///
  /// In fr, this message translates to:
  /// **'Le stock deviendra négatif et sera signalé.'**
  String get resolutionLocaleDetail;

  /// No description provided for @resolutionArbitrage.
  ///
  /// In fr, this message translates to:
  /// **'Demander un arbitrage'**
  String get resolutionArbitrage;

  /// No description provided for @resolutionArbitrageDetail.
  ///
  /// In fr, this message translates to:
  /// **'La décision est renvoyée au conducteur de travaux.'**
  String get resolutionArbitrageDetail;

  /// No description provided for @scanTitre.
  ///
  /// In fr, this message translates to:
  /// **'Lire un code-barres'**
  String get scanTitre;

  /// No description provided for @scanAide.
  ///
  /// In fr, this message translates to:
  /// **'Présentez le code dans le cadre'**
  String get scanAide;

  /// No description provided for @scanIndisponible.
  ///
  /// In fr, this message translates to:
  /// **'Caméra indisponible. Autorisez la caméra dans les réglages du téléphone.'**
  String get scanIndisponible;

  /// No description provided for @codeInconnu.
  ///
  /// In fr, this message translates to:
  /// **'Aucun article ne porte le code {code}.'**
  String codeInconnu(String code);

  /// No description provided for @photoJustificative.
  ///
  /// In fr, this message translates to:
  /// **'Photo justificative'**
  String get photoJustificative;

  /// No description provided for @prendrePhoto.
  ///
  /// In fr, this message translates to:
  /// **'Prendre une photo'**
  String get prendrePhoto;

  /// No description provided for @photoIndisponible.
  ///
  /// In fr, this message translates to:
  /// **'Photo non prise.'**
  String get photoIndisponible;

  /// No description provided for @exporterJournal.
  ///
  /// In fr, this message translates to:
  /// **'Exporter le journal affiché'**
  String get exporterJournal;

  /// No description provided for @exportIndisponible.
  ///
  /// In fr, this message translates to:
  /// **'Export impossible sur cet appareil.'**
  String get exportIndisponible;
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
