// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'traductions.dart';

// ignore_for_file: type=lint

/// The translations for French (`fr`).
class TraductionsFr extends Traductions {
  TraductionsFr([String locale = 'fr']) : super(locale);

  @override
  String get ongletStock => 'Stock';

  @override
  String get ongletFiches => 'Fiches';

  @override
  String get ongletAValider => 'À valider';

  @override
  String get ongletHistorique => 'Historique';

  @override
  String get ongletSynchro => 'Synchro';

  @override
  String get ongletProfil => 'Profil';

  @override
  String get roleMagasinier => 'Magasinier';

  @override
  String get roleTechnicien => 'Technicien';

  @override
  String get roleChefChantier => 'Chef de chantier';

  @override
  String get roleGestionnaireStock => 'Gestionnaire de stock';

  @override
  String get roleResponsableTechnique => 'Responsable technique';

  @override
  String get annuler => 'Annuler';

  @override
  String get changer => 'Changer';

  @override
  String get seConnecter => 'Se connecter';

  @override
  String get synchroniser => 'Synchroniser';

  @override
  String get diminuer => 'Diminuer';

  @override
  String get augmenter => 'Augmenter';

  @override
  String get champObligatoire => 'Ce champ est obligatoire.';

  @override
  String get modeHorsLigneSecurise => 'MODE HORS-LIGNE SÉCURISÉ';

  @override
  String get pinTitre => 'CODE PIN CHANTIER';

  @override
  String get pinAide => 'Saisissez votre code à 6 chiffres';

  @override
  String get pinIncorrect => 'Code incorrect. Réessayez.';

  @override
  String get pinIncomplet => 'Le code compte 6 chiffres.';

  @override
  String get pinRaz => 'Vider';

  @override
  String get pinEffacer => 'Effacer le dernier chiffre';

  @override
  String pinSaisi(int remplis, int total) {
    return '$remplis chiffres saisis sur $total';
  }

  @override
  String get deverrouillageActif => 'Déverrouillage hors-ligne actif';

  @override
  String get donneesSurAppareil => 'Données sécurisées sur l\'appareil';

  @override
  String donneesSynchroniseesLe(String date) {
    return 'Dernière connexion en ligne : $date';
  }

  @override
  String get piedHorsLigne => 'ChantierSync · Mode hors-ligne';

  @override
  String appareil(String id) {
    return 'Appareil $id';
  }

  @override
  String get retirerCompteTitre => 'Retirer ce compte de l\'appareil ?';

  @override
  String get retirerCompteTexte =>
      'Les données enregistrées sur cet appareil seront effacées. Une connexion en ligne sera nécessaire pour revenir.';

  @override
  String get retirerCompteAction => 'Retirer le compte';

  @override
  String retirerCompteAlerte(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other:
          'Attention : $n saisies n\'ont pas encore été envoyées et seront perdues.',
      one: 'Attention : 1 saisie n\'a pas encore été envoyée et sera perdue.',
    );
    return '$_temp0';
  }

  @override
  String get connexionAccroche =>
      'Le chantier dans la poche, même sans réseau.';

  @override
  String get identifiant => 'Identifiant';

  @override
  String get motDePasse => 'Mot de passe';

  @override
  String get afficherMotDePasse => 'Afficher le mot de passe';

  @override
  String get masquerMotDePasse => 'Masquer le mot de passe';

  @override
  String get connexionAide =>
      'Connexion en ligne requise une seule fois, puis accès par code PIN.';

  @override
  String get comptesDemoTitre => 'Comptes de démonstration';

  @override
  String get comptesDemoAide =>
      'Affichés uniquement parce que les données sont simulées. Touchez un profil pour remplir le formulaire.';

  @override
  String get erreurIdentifiants => 'Identifiant ou mot de passe incorrect.';

  @override
  String get erreurCompteInactif =>
      'Ce compte est désactivé. Contactez votre administrateur.';

  @override
  String erreurVerrouille(int secondes) {
    String _temp0 = intl.Intl.pluralLogic(
      secondes,
      locale: localeName,
      other: 'Compte verrouillé. Réessayez dans $secondes secondes.',
      one: 'Compte verrouillé. Réessayez dans 1 seconde.',
      zero: 'Compte temporairement verrouillé après plusieurs échecs.',
    );
    return '$_temp0';
  }

  @override
  String get erreurSansAccesTerrain =>
      'Ce compte n\'a pas d\'accès terrain sur l\'application mobile.';

  @override
  String get infoSessionRevoquee => 'Le compte a été retiré de cet appareil.';

  @override
  String get infoSessionExpiree =>
      'Plus de 14 jours sans connexion en ligne : reconnectez-vous pour continuer.';

  @override
  String get erreurDonneesInaccessibles =>
      'Impossible d\'ouvrir les données de l\'appareil.';

  @override
  String get erreurConnexionImpossible =>
      'Connexion impossible. Vérifiez le réseau puis réessayez.';

  @override
  String get definirCodeTitre => 'Définir mon code';

  @override
  String get definirCodeSousTitre => 'Pour ouvrir l\'application sans réseau';

  @override
  String get choisirCode => 'Choisissez un code';

  @override
  String get choisirCodeAide => '6 chiffres que vous serez seul à connaître.';

  @override
  String get confirmerCode => 'Confirmez le code';

  @override
  String get confirmerCodeAide => 'Saisissez à nouveau le même code.';

  @override
  String get codesDifferents =>
      'Les deux codes ne correspondent pas. Recommencez.';

  @override
  String get synchroAJour => 'Données à jour';

  @override
  String synchroEnAttente(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n éléments en attente d\'envoi',
      one: '1 élément en attente d\'envoi',
    );
    return '$_temp0';
  }

  @override
  String get synchroTitre => 'Synchronisation';

  @override
  String get synchroExplication =>
      'Vos saisies sont enregistrées sur l\'appareil et partent dès que la connexion revient.';

  @override
  String get fileAttenteTitre => 'File d\'attente';

  @override
  String get fileVideTitre => 'Rien à envoyer';

  @override
  String get fileVideTexte =>
      'Les saisies faites sans réseau apparaîtront ici en attendant leur envoi.';

  @override
  String get etatEnAttenteEnvoi => 'En attente';

  @override
  String get etatEnvoye => 'Envoyé';

  @override
  String get signatureTitre => 'Signature par code PIN';

  @override
  String get signatureAide => 'Votre code confirme la décision.';

  @override
  String get moduleEnPreparation => 'Cet espace est en cours d\'installation.';

  @override
  String get profilLangue => 'Langue';

  @override
  String get profilTheme => 'Apparence';

  @override
  String get themeSysteme => 'Automatique';

  @override
  String get themeClair => 'Clair';

  @override
  String get themeSombre => 'Sombre';

  @override
  String get profilSynchroAide => 'File d\'attente et état des envois';

  @override
  String get profilVerrouiller => 'Verrouiller';

  @override
  String get profilVerrouillerAide => 'Revenir à l\'écran du code PIN';

  @override
  String get profilRetirerAide => 'Efface les données de cet appareil';

  @override
  String profilAPropos(String appareil) {
    return 'Schiavone Group · Italia Construction\nAppareil $appareil · version 1.0';
  }
}
