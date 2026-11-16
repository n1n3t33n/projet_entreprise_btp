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

  @override
  String get niveauVide => 'Vide';

  @override
  String get niveauCritique => 'Critique';

  @override
  String get niveauMini => 'Mini';

  @override
  String get niveauPlein => 'Plein';

  @override
  String get stockNegatif => 'Stock négatif';

  @override
  String get stockNegatifExplication =>
      'Le stock est négatif : anomalie à corriger par un inventaire.';

  @override
  String get jaugeCapacite => 'Capacité';

  @override
  String get typeReception => 'Réception';

  @override
  String get typeSortie => 'Sortie';

  @override
  String get typeRetour => 'Retour';

  @override
  String get typePerte => 'Perte ou casse';

  @override
  String get typeAjustement => 'Ajustement d\'inventaire';

  @override
  String get statutEnregistre => 'Enregistré';

  @override
  String get statutAValider => 'À valider';

  @override
  String get statutValide => 'Validé';

  @override
  String get statutRejete => 'Refusé';

  @override
  String get aLInstant => 'à l\'instant';

  @override
  String ilYAMinutes(int n) {
    return 'il y a $n min';
  }

  @override
  String ilYAHeures(int n) {
    return 'il y a $n h';
  }

  @override
  String get aujourdhui => 'Aujourd\'hui';

  @override
  String get hier => 'Hier';

  @override
  String get choisirArticleTitre => 'Choisir un article';

  @override
  String get rechercherArticle => 'Rechercher un article, un code…';

  @override
  String get aucunResultat => 'Aucun article trouvé';

  @override
  String get aucunResultatAide => 'Modifiez la recherche ou le filtre.';

  @override
  String stockActuel(String quantite) {
    return 'stock actuel : $quantite';
  }

  @override
  String get sortieTitre => 'Sortie rapide';

  @override
  String get sortieAide => 'Remettre du matériel à une équipe';

  @override
  String get receptionTitre => 'Réception';

  @override
  String get receptionAide => 'Enregistrer un bon de livraison';

  @override
  String get retourTitre => 'Retour, casse ou perte';

  @override
  String get retourAide => 'Déclarer un surplus ou un matériel abîmé';

  @override
  String get retourCourt => 'Retour / perte';

  @override
  String get saisieSousTitre => 'Enregistré sur l\'appareil';

  @override
  String get saisieArticle => 'Article';

  @override
  String get saisieQuantite => 'Quantité';

  @override
  String get saisieMention => 'Envoi automatique au retour du réseau.';

  @override
  String get saisieIncomplete =>
      'Complétez les champs obligatoires pour valider.';

  @override
  String toutLeStock(String quantite) {
    return 'Tout le stock ($quantite)';
  }

  @override
  String get stockProjete => 'Stock après saisie';

  @override
  String get sortieDestination => 'Destination';

  @override
  String get sortieLogement => 'Logement ou zone de pose';

  @override
  String get sortieCorpsEtat => 'Corps d\'état';

  @override
  String get sortieBeneficiaire => 'Équipe bénéficiaire';

  @override
  String get facultatif => 'Facultatif';

  @override
  String get receptionTracabilite => 'Bon de livraison et fournisseur';

  @override
  String get receptionBon => 'N° de bon de livraison ou de conteneur';

  @override
  String get receptionBonExemple => 'Ex. BL-2026-0589';

  @override
  String get receptionFournisseur => 'Fournisseur';

  @override
  String get receptionEtat => 'État de la livraison';

  @override
  String get receptionConforme => 'Conforme';

  @override
  String get receptionReserves => 'Réserves';

  @override
  String get observations => 'Observations';

  @override
  String get receptionObservationsExemple =>
      'Ex. deux sacs éventrés au déchargement';

  @override
  String get retourNature => 'Nature de la déclaration';

  @override
  String get natureRetour => 'Retour au magasin';

  @override
  String get natureRetourDetail => 'Surplus réintégré au stock';

  @override
  String get natureCasse => 'Casse ou avarie';

  @override
  String get natureCasseDetail => 'Matériel abîmé, inutilisable';

  @override
  String get naturePerte => 'Perte';

  @override
  String get naturePerteDetail => 'Matériel manquant, introuvable';

  @override
  String get retourMotif => 'Motif';

  @override
  String get retourMotifAide => 'Choisir un motif';

  @override
  String get retourObservationsExemple => 'Ex. palette restée sous la pluie';

  @override
  String get motifSurplus => 'Surplus de chantier';

  @override
  String get motifErreurMetre => 'Erreur de métré';

  @override
  String get motifHumidite => 'Sac éventré ou humidité';

  @override
  String get motifChoc => 'Choc ou chute';

  @override
  String get motifIntrouvable => 'Introuvable au comptage';

  @override
  String get motifAutre => 'Autre';

  @override
  String validerSortie(String quantite) {
    return 'Valider la sortie ($quantite)';
  }

  @override
  String enregistrerReception(String quantite) {
    return 'Enregistrer la réception ($quantite)';
  }

  @override
  String validerDeclaration(String quantite) {
    return 'Valider la déclaration ($quantite)';
  }

  @override
  String get mouvementEnregistre => 'Mouvement enregistré sur l\'appareil.';

  @override
  String get controleOk =>
      'Stock suffisant : la saisie laisse l\'article au-dessus de son seuil.';

  @override
  String avertissementSeuil(String reste, String seuil) {
    return 'Stock restant $reste, sous le seuil mini de $seuil.';
  }

  @override
  String get avertissementNegatif =>
      'Cette saisie rend le stock négatif. Elle sera signalée comme anomalie.';

  @override
  String get registreTitre => 'Registre du stock';

  @override
  String get registreSousTitre => 'Quantités connues de l\'appareil';

  @override
  String get references => 'références';

  @override
  String get nouveauMouvement => 'Nouveau mouvement';

  @override
  String get filtreTous => 'Tous';

  @override
  String get filtreSousSeuil => 'Sous seuil';

  @override
  String get filtreSorties => 'Sorties';

  @override
  String get filtreEntrees => 'Entrées';

  @override
  String seuilMini(String seuil) {
    return 'Seuil mini : $seuil';
  }

  @override
  String seuilMiniEcart(String seuil, String ecart) {
    return 'Seuil mini : $seuil ($ecart)';
  }

  @override
  String stockConforme(String seuil) {
    return 'Stock conforme (mini : $seuil)';
  }

  @override
  String get ficheArticleTitre => 'Fiche article';

  @override
  String disponibles(String unite) {
    return '$unite en stock';
  }

  @override
  String get mouvementsRecents => 'Mouvements récents';

  @override
  String get journalComplet => 'Journal complet';

  @override
  String get aucunMouvement => 'Aucun mouvement';

  @override
  String get aucunMouvementAide =>
      'Les sorties, réceptions et retours apparaîtront ici.';

  @override
  String get codeBarres => 'Code-barres';

  @override
  String get journalTitre => 'Journal des mouvements';

  @override
  String get journalSousTitre => 'Entrées et sorties du magasin';

  @override
  String get journalRecherche => 'Rechercher un bon, un article, une personne…';

  @override
  String get mouvementsDuJour => 'mouvements du jour';

  @override
  String get entreesDuJour => 'entrées du jour';

  @override
  String get journalNonModifiable => 'Journal horodaté et non modifiable';

  @override
  String get validationTitre => 'Validations';

  @override
  String get validationSousTitre => 'Sorties de stock et alertes';

  @override
  String get ongletDemandes => 'Demandes';

  @override
  String get ongletAlertes => 'Alertes de seuil';

  @override
  String get aucuneDemande => 'Aucune sortie à valider';

  @override
  String get aucuneDemandeAide =>
      'Les sorties saisies par les magasiniers apparaîtront ici.';

  @override
  String get aucuneAlerte => 'Aucune alerte';

  @override
  String get aucuneAlerteAide =>
      'Tous les articles sont au-dessus de leur seuil.';

  @override
  String get materiau => 'Matériau';

  @override
  String get demandeur => 'Saisi par';

  @override
  String get affectation => 'Destination';

  @override
  String get rejeter => 'Refuser';

  @override
  String get approuver => 'Approuver';

  @override
  String signatureSortie(String numero, String quantite) {
    return 'Approuver la sortie $numero ($quantite).';
  }

  @override
  String get sortieApprouvee => 'Sortie approuvée.';

  @override
  String get sortieRefusee => 'Sortie refusée : la quantité revient en stock.';

  @override
  String get separationFonctions =>
      'Vous avez saisi cette opération : une autre personne doit la valider.';

  @override
  String get stockRestant => 'Stock restant :';

  @override
  String get inventaireTitre => 'Inventaire tournant';

  @override
  String get inventaireEnCours => 'En cours';

  @override
  String inventaireProgression(int faits, int total) {
    String _temp0 = intl.Intl.pluralLogic(
      faits,
      locale: localeName,
      other: '$faits articles comptés',
      one: '1 article compté',
    );
    return '$_temp0 sur $total';
  }

  @override
  String get articleEnControle => 'Article à compter';

  @override
  String get stockTheorique => 'Stock attendu';

  @override
  String get quantiteComptee => 'Quantité comptée';

  @override
  String ecartDetecte(String ecart) {
    return 'Écart constaté : $ecart. Justification obligatoire.';
  }

  @override
  String get ecartChutes => 'Chutes de coupe';

  @override
  String get ecartRebut => 'Matériel au rebut';

  @override
  String get ecartNonDeclare => 'Mouvement non déclaré';

  @override
  String get ecartRecompter => 'Comptage à refaire';

  @override
  String get justificationObligatoire =>
      'Choisissez une justification pour l\'écart.';

  @override
  String validerArticle(String quantite) {
    return 'Valider $quantite et passer au suivant';
  }

  @override
  String get soumettreInventaire => 'Soumettre l\'inventaire à validation';

  @override
  String get inventaireSoumis => 'Inventaire transmis pour validation.';

  @override
  String get validerInventaire => 'Valider l\'inventaire';

  @override
  String get inventaireValide => 'Inventaire validé : le stock a été ajusté.';

  @override
  String get inventaireRegle =>
      'Le stock n\'est ajusté qu\'après cette validation.';

  @override
  String signatureInventaire(String id, int n) {
    return 'Valider l\'inventaire $id et ajuster le stock ($n écarts).';
  }

  @override
  String get inventaireEnAttenteValidation =>
      'Comptage terminé. L\'inventaire attend la validation du gestionnaire de stock.';

  @override
  String get inventaireArticles => 'Articles de la zone';

  @override
  String get inventaireAValider => 'Inventaire à valider';

  @override
  String inventaireEcarts(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n écarts à examiner',
      one: '1 écart à examiner',
      zero: 'Aucun écart',
    );
    return '$_temp0';
  }

  @override
  String get aCompter => 'À compter';

  @override
  String get conforme => 'Conforme';

  @override
  String get alertesPriorites => 'Alertes et priorités';

  @override
  String voirToutesAlertes(int n) {
    return 'Voir les $n alertes';
  }

  @override
  String get stockMagasin => 'Stock du magasin';

  @override
  String get sousSeuil => 'sous seuil';

  @override
  String get consulterStock => 'Consulter le stock';

  @override
  String get consulterRegistre => 'Consulter le registre';

  @override
  String get raccourcis => 'Raccourcis';

  @override
  String get reprendreComptage => 'Reprendre le comptage';

  @override
  String get suivreInventaire => 'Suivre le comptage';

  @override
  String get mouvements24h => 'mouv. sur 24 h';

  @override
  String get sortiesAValider => 'Sorties à valider';

  @override
  String nombreDemandes(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n demandes',
      one: '1 demande',
      zero: 'À jour',
    );
    return '$_temp0';
  }

  @override
  String examinerSorties(int n) {
    return 'Examiner les $n sorties';
  }

  @override
  String get etapeAFaire => 'À faire';

  @override
  String get etapeEnCours => 'En cours';

  @override
  String get etapeADeclaree => 'À valider';

  @override
  String get etapeValidee => 'Validée';

  @override
  String get etapeBloquee => 'Bloquée';

  @override
  String get etapesFaites => 'terminées';

  @override
  String get filtreToutes => 'Toutes';

  @override
  String get evDemarrage => 'Démarrage';

  @override
  String get evPointage => 'Pointage';

  @override
  String get evPause => 'Pause';

  @override
  String get evReprise => 'Reprise';

  @override
  String get evBlocage => 'Blocage';

  @override
  String get evLeveeBlocage => 'Blocage levé';

  @override
  String get evFin => 'Fin déclarée';

  @override
  String get evValidation => 'Validation';

  @override
  String get evRejet => 'Reprise demandée';

  @override
  String get evReaffectation => 'Réaffectation';

  @override
  String get blocageRupture => 'Rupture de matériau';

  @override
  String get blocagePanne => 'Panne d\'engin ou d\'outillage';

  @override
  String get blocageIntemperies => 'Intempéries';

  @override
  String get blocageNonConformite => 'Non-conformité du support';

  @override
  String get blocageAcces => 'Accès au chantier bloqué';

  @override
  String get graviteArret => 'Arrêt total';

  @override
  String get graviteRalenti => 'Ralenti';

  @override
  String get graviteAlerte => 'Simple alerte';

  @override
  String get retardDeuxHeures => '2 heures';

  @override
  String get retardDemiJournee => 'Demi-journée';

  @override
  String get retardUnJour => 'Un jour ou plus';

  @override
  String get ficheRouteTitre => 'Fiche de route';

  @override
  String get progressionJour => 'Progression du jour';

  @override
  String etapesTerminees(int faits, int total) {
    return '$faits étapes terminées sur $total';
  }

  @override
  String get aucuneEtape => 'Aucune étape';

  @override
  String get aucuneEtapeAide => 'Aucune étape ne correspond pour le moment.';

  @override
  String etapeTitre(String id) {
    return 'Étape $id';
  }

  @override
  String get actionImpossible =>
      'Action impossible dans l\'état actuel de l\'étape.';

  @override
  String get demarrerEtape => 'Démarrer l\'étape';

  @override
  String validerPointage(String valeur) {
    return 'Enregistrer le pointage ($valeur)';
  }

  @override
  String get pointageEnregistre => 'Pointage enregistré sur l\'appareil.';

  @override
  String get terminerEtape => 'Déclarer l\'étape terminée';

  @override
  String get etapeDeclaree =>
      'Étape déclarée terminée : elle attend sa validation.';

  @override
  String get terminerMention => 'Une autre personne devra valider l\'étape.';

  @override
  String get terminerConditions =>
      'Pour terminer : métré atteint et tous les contrôles cochés.';

  @override
  String get leverBlocage => 'Lever le blocage';

  @override
  String get journalEtapeTitre => 'Journal d\'étape';

  @override
  String get journalEtapeSousTitre => 'Activité horodatée';

  @override
  String get localisation => 'Localisation';

  @override
  String get pointageActif => 'POINTAGE EN COURS';

  @override
  String get pointageArrete => 'POINTAGE EN PAUSE';

  @override
  String get mettreEnPause => 'Mettre en pause';

  @override
  String get reprendre => 'Reprendre';

  @override
  String get avancementMetre => 'Avancement du métré';

  @override
  String cible(String valeur) {
    return 'Cible : $valeur';
  }

  @override
  String surCible(String valeur) {
    return 'sur $valeur';
  }

  @override
  String get solde => 'Solde total';

  @override
  String get gammeSecurite => 'Gamme opératoire et sécurité';

  @override
  String get declarerBlocage => 'Déclarer un blocage';

  @override
  String get reaffecterEtape => 'Réaffecter à une autre équipe';

  @override
  String get blocageTitre => 'Déclarer un blocage';

  @override
  String get blocageMention =>
      'L\'alerte part vers le bureau dès que la connexion revient.';

  @override
  String get transmettreBlocage => 'Transmettre l\'alerte de blocage';

  @override
  String get blocageTransmis => 'Blocage enregistré : l\'étape est arrêtée.';

  @override
  String get blocageNature => 'Nature du blocage';

  @override
  String get blocageArticle => 'Désigner l\'article manquant';

  @override
  String get blocageGravite => 'Gravité';

  @override
  String get blocageRetard => 'Retard estimé';

  @override
  String get blocageObservationsExemple =>
      'Ex. livraison de ciment retardée de 3 h';

  @override
  String get controlesTitre => 'Contrôles et réception';

  @override
  String get controlesSousTitre => 'Étapes déclarées terminées';

  @override
  String signatureEtape(String id, String libelle) {
    return 'Valider l\'étape $id : $libelle.';
  }

  @override
  String get etapeValideeMessage => 'Étape validée.';

  @override
  String get etapeRefuseeMessage =>
      'Reprise demandée : l\'étape repasse en cours.';

  @override
  String get aucunControle => 'Aucune étape à valider';

  @override
  String get aucunControleAide =>
      'Les étapes déclarées terminées apparaîtront ici.';

  @override
  String declarePar(String nom) {
    return 'Déclarée terminée par $nom';
  }

  @override
  String get validerEtape => 'Valider';

  @override
  String get reaffectationTitre => 'Réaffectation';

  @override
  String get reaffectationMention =>
      'La nouvelle équipe verra l\'étape sur sa fiche de route.';

  @override
  String get confirmerReaffectation => 'Confirmer la réaffectation';

  @override
  String reaffectationFaite(String equipe) {
    return 'Étape confiée à $equipe.';
  }

  @override
  String get reaffectationMotif => 'Motif';

  @override
  String get motifRetardPlanning => 'Retard de planning';

  @override
  String get motifAbsence => 'Absence d\'ouvriers';

  @override
  String get motifCompetence => 'Compétence requise';

  @override
  String get motifSurcroit => 'Surcroît d\'activité';

  @override
  String get reaffectationEquipe => 'Nouvelle équipe';

  @override
  String equipeDetail(String chef, int n) {
    return 'Chef : $chef · $n ouvriers';
  }

  @override
  String get chargeActuelle => 'Charge';

  @override
  String get reaffectationConsigne => 'Consigne de transmission';

  @override
  String get reaffectationConsigneExemple =>
      'Ex. coffrage prêt, attendre la livraison du béton';

  @override
  String get dureePointee => 'temps pointé';

  @override
  String get evenementsTraces => 'événements tracés';

  @override
  String get aucunEvenement => 'Aucune activité';

  @override
  String get aucunEvenementAide =>
      'Les démarrages, pointages et validations apparaîtront ici.';

  @override
  String pourcentRealise(int n) {
    return '$n % réalisé';
  }

  @override
  String get ouvrirFicheRoute => 'Ouvrir la fiche de route';

  @override
  String get maFicheDuJour => 'Ma fiche de route du jour';

  @override
  String get pointageRapide => 'Pointage rapide';

  @override
  String get prochainesEtapes => 'Prochaines étapes';

  @override
  String get aValiderPriorite => 'À valider en priorité';

  @override
  String nombreActions(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n actions',
      one: '1 action',
      zero: 'À jour',
    );
    return '$_temp0';
  }

  @override
  String get sortiesAValiderDetail => 'Bons de matériel du magasin';

  @override
  String get etapesAControler => 'Étapes à contrôler';

  @override
  String get etapesAControlerDetail => 'Travaux déclarés terminés';

  @override
  String nombreEtapes(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n étapes',
      one: '1 étape',
      zero: 'Aucune étape',
    );
    return '$_temp0';
  }

  @override
  String get blocagesPrioritaires => 'Blocages en cours';

  @override
  String get aucunBlocage => 'Aucune étape bloquée.';

  @override
  String get supervisionTravaux => 'Supervision des travaux et conformité';

  @override
  String get visasTechniques => 'Visas techniques';

  @override
  String get examinerEtapes => 'Examiner les étapes';

  @override
  String get syntheseChantier => 'Synthèse par corps d\'état';

  @override
  String etapesValideesSur(int faits, int total) {
    return '$faits étapes validées sur $total';
  }

  @override
  String get outilsPosteFixe => 'Outils complets sur poste fixe';

  @override
  String get outilsPosteFixeAide =>
      'Plannings, équipes et exports se pilotent depuis le poste de pilotage web.';

  @override
  String synchroTerminee(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n éléments envoyés.',
      one: '1 élément envoyé.',
      zero: 'Rien à envoyer.',
    );
    return '$_temp0';
  }

  @override
  String get derniereSynchro => 'Dernière synchronisation';

  @override
  String get jamais => 'Jamais';

  @override
  String get synchroniserMaintenant => 'Synchroniser maintenant';

  @override
  String get conflitsTitre => 'Écarts à arbitrer';

  @override
  String get conflitExplication =>
      'La quantité saisie sur l\'appareil dépasse ce que le serveur connaît.';

  @override
  String get cetAppareil => 'Sortie saisie ici';

  @override
  String get serveur => 'Stock connu du bureau';

  @override
  String get resolutionServeur => 'Suivre le bureau (recommandé)';

  @override
  String get resolutionServeurDetail =>
      'La sortie est ramenée à la quantité disponible.';

  @override
  String get resolutionLocale => 'Garder la saisie du terrain';

  @override
  String get resolutionLocaleDetail =>
      'Le stock deviendra négatif et sera signalé.';

  @override
  String get resolutionArbitrage => 'Demander un arbitrage';

  @override
  String get resolutionArbitrageDetail =>
      'La décision est renvoyée au conducteur de travaux.';

  @override
  String get scanTitre => 'Lire un code-barres';

  @override
  String get scanAide => 'Présentez le code dans le cadre';

  @override
  String get scanIndisponible =>
      'Caméra indisponible. Autorisez la caméra dans les réglages du téléphone.';

  @override
  String codeInconnu(String code) {
    return 'Aucun article ne porte le code $code.';
  }

  @override
  String get photoJustificative => 'Photo justificative';

  @override
  String get prendrePhoto => 'Prendre une photo';

  @override
  String get photoIndisponible => 'Photo non prise.';

  @override
  String get exporterJournal => 'Exporter le journal affiché';

  @override
  String get exportIndisponible => 'Export impossible sur cet appareil.';
}
