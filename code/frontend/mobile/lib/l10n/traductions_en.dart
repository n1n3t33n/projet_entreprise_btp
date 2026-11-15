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

  @override
  String get niveauVide => 'Empty';

  @override
  String get niveauCritique => 'Critical';

  @override
  String get niveauMini => 'Low';

  @override
  String get niveauPlein => 'Full';

  @override
  String get stockNegatif => 'Negative stock';

  @override
  String get stockNegatifExplication =>
      'Stock is negative: an anomaly to fix with a stock count.';

  @override
  String get jaugeCapacite => 'Capacity';

  @override
  String get typeReception => 'Delivery';

  @override
  String get typeSortie => 'Issue';

  @override
  String get typeRetour => 'Return';

  @override
  String get typePerte => 'Loss or breakage';

  @override
  String get typeAjustement => 'Stock count adjustment';

  @override
  String get statutEnregistre => 'Recorded';

  @override
  String get statutAValider => 'To approve';

  @override
  String get statutValide => 'Approved';

  @override
  String get statutRejete => 'Rejected';

  @override
  String get aLInstant => 'just now';

  @override
  String ilYAMinutes(int n) {
    return '$n min ago';
  }

  @override
  String ilYAHeures(int n) {
    return '$n h ago';
  }

  @override
  String get aujourdhui => 'Today';

  @override
  String get hier => 'Yesterday';

  @override
  String get choisirArticleTitre => 'Choose an item';

  @override
  String get rechercherArticle => 'Search an item, a code…';

  @override
  String get aucunResultat => 'No item found';

  @override
  String get aucunResultatAide => 'Change the search or the filter.';

  @override
  String stockActuel(String quantite) {
    return 'current stock: $quantite';
  }

  @override
  String get sortieTitre => 'Quick issue';

  @override
  String get sortieAide => 'Hand materials over to a crew';

  @override
  String get receptionTitre => 'Delivery';

  @override
  String get receptionAide => 'Record a delivery note';

  @override
  String get retourTitre => 'Return, breakage or loss';

  @override
  String get retourAide => 'Report a surplus or damaged materials';

  @override
  String get retourCourt => 'Return / loss';

  @override
  String get saisieSousTitre => 'Saved on this device';

  @override
  String get saisieArticle => 'Item';

  @override
  String get saisieQuantite => 'Quantity';

  @override
  String get saisieMention => 'Sent automatically when the network is back.';

  @override
  String get saisieIncomplete => 'Fill in the required fields to confirm.';

  @override
  String toutLeStock(String quantite) {
    return 'All the stock ($quantite)';
  }

  @override
  String get stockProjete => 'Stock after entry';

  @override
  String get sortieDestination => 'Destination';

  @override
  String get sortieLogement => 'Housing unit or work area';

  @override
  String get sortieCorpsEtat => 'Trade';

  @override
  String get sortieBeneficiaire => 'Receiving crew';

  @override
  String get facultatif => 'Optional';

  @override
  String get receptionTracabilite => 'Delivery note and supplier';

  @override
  String get receptionBon => 'Delivery note or container number';

  @override
  String get receptionBonExemple => 'E.g. BL-2026-0589';

  @override
  String get receptionFournisseur => 'Supplier';

  @override
  String get receptionEtat => 'Delivery condition';

  @override
  String get receptionConforme => 'Compliant';

  @override
  String get receptionReserves => 'With reservations';

  @override
  String get observations => 'Remarks';

  @override
  String get receptionObservationsExemple =>
      'E.g. two bags torn while unloading';

  @override
  String get retourNature => 'Type of report';

  @override
  String get natureRetour => 'Return to the store';

  @override
  String get natureRetourDetail => 'Surplus put back into stock';

  @override
  String get natureCasse => 'Breakage or damage';

  @override
  String get natureCasseDetail => 'Damaged, unusable materials';

  @override
  String get naturePerte => 'Loss';

  @override
  String get naturePerteDetail => 'Missing materials, not found';

  @override
  String get retourMotif => 'Reason';

  @override
  String get retourMotifAide => 'Choose a reason';

  @override
  String get retourObservationsExemple => 'E.g. pallet left out in the rain';

  @override
  String get motifSurplus => 'Site surplus';

  @override
  String get motifErreurMetre => 'Take-off error';

  @override
  String get motifHumidite => 'Torn bag or moisture';

  @override
  String get motifChoc => 'Impact or fall';

  @override
  String get motifIntrouvable => 'Not found when counting';

  @override
  String get motifAutre => 'Other';

  @override
  String validerSortie(String quantite) {
    return 'Confirm the issue ($quantite)';
  }

  @override
  String enregistrerReception(String quantite) {
    return 'Record the delivery ($quantite)';
  }

  @override
  String validerDeclaration(String quantite) {
    return 'Confirm the report ($quantite)';
  }

  @override
  String get mouvementEnregistre => 'Movement saved on this device.';

  @override
  String get controleOk =>
      'Enough stock: the entry keeps the item above its threshold.';

  @override
  String avertissementSeuil(String reste, String seuil) {
    return 'Remaining stock $reste, below the minimum of $seuil.';
  }

  @override
  String get avertissementNegatif =>
      'This entry makes the stock negative. It will be flagged as an anomaly.';

  @override
  String get registreTitre => 'Stock register';

  @override
  String get registreSousTitre => 'Quantities known to this device';

  @override
  String get references => 'items';

  @override
  String get nouveauMouvement => 'New movement';

  @override
  String get filtreTous => 'All';

  @override
  String get filtreSousSeuil => 'Below threshold';

  @override
  String get filtreSorties => 'Issues';

  @override
  String get filtreEntrees => 'Receipts';

  @override
  String seuilMini(String seuil) {
    return 'Minimum: $seuil';
  }

  @override
  String seuilMiniEcart(String seuil, String ecart) {
    return 'Minimum: $seuil ($ecart)';
  }

  @override
  String stockConforme(String seuil) {
    return 'Stock OK (minimum: $seuil)';
  }

  @override
  String get ficheArticleTitre => 'Item sheet';

  @override
  String disponibles(String unite) {
    return '$unite in stock';
  }

  @override
  String get mouvementsRecents => 'Recent movements';

  @override
  String get journalComplet => 'Full log';

  @override
  String get aucunMouvement => 'No movement';

  @override
  String get aucunMouvementAide =>
      'Issues, deliveries and returns will appear here.';

  @override
  String get codeBarres => 'Barcode';

  @override
  String get journalTitre => 'Movement log';

  @override
  String get journalSousTitre => 'Store receipts and issues';

  @override
  String get journalRecherche => 'Search a note, an item, a person…';

  @override
  String get mouvementsDuJour => 'movements today';

  @override
  String get entreesDuJour => 'receipts today';

  @override
  String get journalNonModifiable => 'Time-stamped log, cannot be edited';

  @override
  String get validationTitre => 'Approvals';

  @override
  String get validationSousTitre => 'Stock issues and alerts';

  @override
  String get ongletDemandes => 'Requests';

  @override
  String get ongletAlertes => 'Threshold alerts';

  @override
  String get aucuneDemande => 'No issue to approve';

  @override
  String get aucuneDemandeAide =>
      'Issues entered by storekeepers will appear here.';

  @override
  String get aucuneAlerte => 'No alert';

  @override
  String get aucuneAlerteAide => 'All items are above their threshold.';

  @override
  String get materiau => 'Material';

  @override
  String get demandeur => 'Entered by';

  @override
  String get affectation => 'Destination';

  @override
  String get rejeter => 'Reject';

  @override
  String get approuver => 'Approve';

  @override
  String signatureSortie(String numero, String quantite) {
    return 'Approve issue $numero ($quantite).';
  }

  @override
  String get sortieApprouvee => 'Issue approved.';

  @override
  String get sortieRefusee =>
      'Issue rejected: the quantity goes back into stock.';

  @override
  String get separationFonctions =>
      'You entered this operation: another person must approve it.';

  @override
  String get stockRestant => 'Remaining stock:';

  @override
  String get inventaireTitre => 'Cycle count';

  @override
  String get inventaireEnCours => 'In progress';

  @override
  String inventaireProgression(int faits, int total) {
    String _temp0 = intl.Intl.pluralLogic(
      faits,
      locale: localeName,
      other: '$faits items counted',
      one: '1 item counted',
    );
    return '$_temp0 out of $total';
  }

  @override
  String get articleEnControle => 'Item to count';

  @override
  String get stockTheorique => 'Expected stock';

  @override
  String get quantiteComptee => 'Counted quantity';

  @override
  String ecartDetecte(String ecart) {
    return 'Difference found: $ecart. A reason is required.';
  }

  @override
  String get ecartChutes => 'Offcuts';

  @override
  String get ecartRebut => 'Scrapped materials';

  @override
  String get ecartNonDeclare => 'Unreported movement';

  @override
  String get ecartRecompter => 'Recount needed';

  @override
  String get justificationObligatoire => 'Choose a reason for the difference.';

  @override
  String validerArticle(String quantite) {
    return 'Confirm $quantite and go to next';
  }

  @override
  String get soumettreInventaire => 'Submit the count for approval';

  @override
  String get inventaireSoumis => 'Count submitted for approval.';

  @override
  String get validerInventaire => 'Approve the count';

  @override
  String get inventaireValide => 'Count approved: stock has been adjusted.';

  @override
  String get inventaireRegle => 'Stock is adjusted only after this approval.';

  @override
  String signatureInventaire(String id, int n) {
    return 'Approve count $id and adjust the stock ($n differences).';
  }

  @override
  String get inventaireEnAttenteValidation =>
      'Counting is done. The count is waiting for the stock controller\'s approval.';

  @override
  String get inventaireArticles => 'Items in the area';

  @override
  String get inventaireAValider => 'Count to approve';

  @override
  String inventaireEcarts(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n differences to review',
      one: '1 difference to review',
      zero: 'No difference',
    );
    return '$_temp0';
  }

  @override
  String get aCompter => 'To count';

  @override
  String get conforme => 'OK';

  @override
  String get alertesPriorites => 'Alerts and priorities';

  @override
  String voirToutesAlertes(int n) {
    return 'See all $n alerts';
  }

  @override
  String get stockMagasin => 'Store stock';

  @override
  String get sousSeuil => 'below threshold';

  @override
  String get consulterStock => 'View stock';

  @override
  String get consulterRegistre => 'Open the register';

  @override
  String get raccourcis => 'Shortcuts';

  @override
  String get reprendreComptage => 'Resume counting';

  @override
  String get suivreInventaire => 'Follow the count';

  @override
  String get mouvements24h => 'moves in 24 h';

  @override
  String get sortiesAValider => 'Issues to approve';

  @override
  String nombreDemandes(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n requests',
      one: '1 request',
      zero: 'Up to date',
    );
    return '$_temp0';
  }

  @override
  String examinerSorties(int n) {
    return 'Review the $n issues';
  }

  @override
  String get etapeAFaire => 'To do';

  @override
  String get etapeEnCours => 'In progress';

  @override
  String get etapeADeclaree => 'To approve';

  @override
  String get etapeValidee => 'Approved';

  @override
  String get etapeBloquee => 'Blocked';

  @override
  String get etapesFaites => 'done';

  @override
  String get filtreToutes => 'All';

  @override
  String get evDemarrage => 'Start';

  @override
  String get evPointage => 'Progress update';

  @override
  String get evPause => 'Pause';

  @override
  String get evReprise => 'Resume';

  @override
  String get evBlocage => 'Blocked';

  @override
  String get evLeveeBlocage => 'Unblocked';

  @override
  String get evFin => 'Declared done';

  @override
  String get evValidation => 'Approval';

  @override
  String get evRejet => 'Rework requested';

  @override
  String get evReaffectation => 'Reassignment';

  @override
  String get blocageRupture => 'Material shortage';

  @override
  String get blocagePanne => 'Machine or tool breakdown';

  @override
  String get blocageIntemperies => 'Bad weather';

  @override
  String get blocageNonConformite => 'Non-compliant substrate';

  @override
  String get blocageAcces => 'Site access blocked';

  @override
  String get graviteArret => 'Full stop';

  @override
  String get graviteRalenti => 'Slowed down';

  @override
  String get graviteAlerte => 'Warning only';

  @override
  String get retardDeuxHeures => '2 hours';

  @override
  String get retardDemiJournee => 'Half a day';

  @override
  String get retardUnJour => 'A day or more';

  @override
  String get ficheRouteTitre => 'Work sheet';

  @override
  String get progressionJour => 'Today\'s progress';

  @override
  String etapesTerminees(int faits, int total) {
    return '$faits of $total steps done';
  }

  @override
  String get aucuneEtape => 'No step';

  @override
  String get aucuneEtapeAide => 'No step matches for now.';

  @override
  String etapeTitre(String id) {
    return 'Step $id';
  }

  @override
  String get actionImpossible =>
      'This action is not possible in the step\'s current state.';

  @override
  String get demarrerEtape => 'Start the step';

  @override
  String validerPointage(String valeur) {
    return 'Save progress ($valeur)';
  }

  @override
  String get pointageEnregistre => 'Progress saved on this device.';

  @override
  String get terminerEtape => 'Declare the step done';

  @override
  String get etapeDeclaree => 'Step declared done: waiting for approval.';

  @override
  String get terminerMention => 'Another person will have to approve the step.';

  @override
  String get terminerConditions =>
      'To finish: target reached and all checks ticked.';

  @override
  String get leverBlocage => 'Remove the block';

  @override
  String get journalEtapeTitre => 'Step log';

  @override
  String get journalEtapeSousTitre => 'Time-stamped activity';

  @override
  String get localisation => 'Location';

  @override
  String get pointageActif => 'TIME TRACKING ON';

  @override
  String get pointageArrete => 'TIME TRACKING PAUSED';

  @override
  String get mettreEnPause => 'Pause';

  @override
  String get reprendre => 'Resume';

  @override
  String get avancementMetre => 'Quantity progress';

  @override
  String cible(String valeur) {
    return 'Target: $valeur';
  }

  @override
  String surCible(String valeur) {
    return 'out of $valeur';
  }

  @override
  String get solde => 'All remaining';

  @override
  String get gammeSecurite => 'Method and safety checks';

  @override
  String get declarerBlocage => 'Report a blocker';

  @override
  String get reaffecterEtape => 'Reassign to another crew';

  @override
  String get blocageTitre => 'Report a blocker';

  @override
  String get blocageMention =>
      'The alert is sent to the office as soon as the connection is back.';

  @override
  String get transmettreBlocage => 'Send the blocker alert';

  @override
  String get blocageTransmis => 'Blocker saved: the step is stopped.';

  @override
  String get blocageNature => 'Type of blocker';

  @override
  String get blocageArticle => 'Select the missing item';

  @override
  String get blocageGravite => 'Severity';

  @override
  String get blocageRetard => 'Estimated delay';

  @override
  String get blocageObservationsExemple => 'E.g. cement delivery 3 h late';

  @override
  String get controlesTitre => 'Checks and acceptance';

  @override
  String get controlesSousTitre => 'Steps declared done';

  @override
  String signatureEtape(String id, String libelle) {
    return 'Approve step $id: $libelle.';
  }

  @override
  String get etapeValideeMessage => 'Step approved.';

  @override
  String get etapeRefuseeMessage =>
      'Rework requested: the step is in progress again.';

  @override
  String get aucunControle => 'No step to approve';

  @override
  String get aucunControleAide => 'Steps declared done will appear here.';

  @override
  String declarePar(String nom) {
    return 'Declared done by $nom';
  }

  @override
  String get validerEtape => 'Approve';

  @override
  String get reaffectationTitre => 'Reassignment';

  @override
  String get reaffectationMention =>
      'The new crew will see the step on its work sheet.';

  @override
  String get confirmerReaffectation => 'Confirm reassignment';

  @override
  String reaffectationFaite(String equipe) {
    return 'Step handed over to $equipe.';
  }

  @override
  String get reaffectationMotif => 'Reason';

  @override
  String get motifRetardPlanning => 'Schedule delay';

  @override
  String get motifAbsence => 'Workers absent';

  @override
  String get motifCompetence => 'Skill required';

  @override
  String get motifSurcroit => 'Workload peak';

  @override
  String get reaffectationEquipe => 'New crew';

  @override
  String equipeDetail(String chef, int n) {
    return 'Lead: $chef · $n workers';
  }

  @override
  String get chargeActuelle => 'Workload';

  @override
  String get reaffectationConsigne => 'Handover note';

  @override
  String get reaffectationConsigneExemple =>
      'E.g. formwork ready, wait for the concrete delivery';

  @override
  String get dureePointee => 'time tracked';

  @override
  String get evenementsTraces => 'events logged';

  @override
  String get aucunEvenement => 'No activity';

  @override
  String get aucunEvenementAide =>
      'Starts, progress updates and approvals will appear here.';

  @override
  String pourcentRealise(int n) {
    return '$n% done';
  }

  @override
  String get ouvrirFicheRoute => 'Open the work sheet';

  @override
  String get maFicheDuJour => 'My work sheet today';

  @override
  String get pointageRapide => 'Quick progress update';

  @override
  String get prochainesEtapes => 'Next steps';

  @override
  String get aValiderPriorite => 'To approve first';

  @override
  String nombreActions(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n actions',
      one: '1 action',
      zero: 'Up to date',
    );
    return '$_temp0';
  }

  @override
  String get sortiesAValiderDetail => 'Store material notes';

  @override
  String get etapesAControler => 'Steps to check';

  @override
  String get etapesAControlerDetail => 'Work declared done';

  @override
  String nombreEtapes(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n steps',
      one: '1 step',
      zero: 'No step',
    );
    return '$_temp0';
  }

  @override
  String get blocagesPrioritaires => 'Current blockers';

  @override
  String get aucunBlocage => 'No blocked step.';

  @override
  String get supervisionTravaux => 'Works supervision and compliance';

  @override
  String get visasTechniques => 'Technical approvals';

  @override
  String get examinerEtapes => 'Review the steps';

  @override
  String get syntheseChantier => 'Summary by trade';

  @override
  String etapesValideesSur(int faits, int total) {
    return '$faits of $total steps approved';
  }

  @override
  String get outilsPosteFixe => 'Full tools on desktop';

  @override
  String get outilsPosteFixeAide =>
      'Schedules, crews and exports are managed from the web control desk.';

  @override
  String synchroTerminee(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n items sent.',
      one: '1 item sent.',
      zero: 'Nothing to send.',
    );
    return '$_temp0';
  }

  @override
  String get derniereSynchro => 'Last synchronisation';

  @override
  String get jamais => 'Never';

  @override
  String get synchroniserMaintenant => 'Sync now';

  @override
  String get conflitsTitre => 'Differences to settle';

  @override
  String get conflitExplication =>
      'The quantity entered on this device is more than the server knows.';

  @override
  String get cetAppareil => 'Issue entered here';

  @override
  String get serveur => 'Stock known to the office';

  @override
  String get resolutionServeur => 'Follow the office (recommended)';

  @override
  String get resolutionServeurDetail =>
      'The issue is reduced to the available quantity.';

  @override
  String get resolutionLocale => 'Keep the field entry';

  @override
  String get resolutionLocaleDetail =>
      'Stock will become negative and will be flagged.';

  @override
  String get resolutionArbitrage => 'Ask for a decision';

  @override
  String get resolutionArbitrageDetail =>
      'The decision is sent to the site supervisor.';
}
