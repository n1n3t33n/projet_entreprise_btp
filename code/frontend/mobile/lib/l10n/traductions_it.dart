// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'traductions.dart';

// ignore_for_file: type=lint

/// The translations for Italian (`it`).
class TraductionsIt extends Traductions {
  TraductionsIt([String locale = 'it']) : super(locale);

  @override
  String get ongletStock => 'Magazzino';

  @override
  String get ongletFiches => 'Schede';

  @override
  String get ongletAValider => 'Da validare';

  @override
  String get ongletHistorique => 'Storico';

  @override
  String get ongletSynchro => 'Sincro';

  @override
  String get ongletProfil => 'Profilo';

  @override
  String get roleMagasinier => 'Magazziniere';

  @override
  String get roleTechnicien => 'Tecnico';

  @override
  String get roleChefChantier => 'Capocantiere';

  @override
  String get roleGestionnaireStock => 'Responsabile di magazzino';

  @override
  String get roleResponsableTechnique => 'Responsabile tecnico';

  @override
  String get annuler => 'Annulla';

  @override
  String get changer => 'Cambia';

  @override
  String get seConnecter => 'Accedi';

  @override
  String get synchroniser => 'Sincronizza';

  @override
  String get diminuer => 'Diminuisci';

  @override
  String get augmenter => 'Aumenta';

  @override
  String get champObligatoire => 'Questo campo è obbligatorio.';

  @override
  String get modeHorsLigneSecurise => 'MODALITÀ OFFLINE SICURA';

  @override
  String get pinTitre => 'CODICE PIN CANTIERE';

  @override
  String get pinAide => 'Inserisci il tuo codice di 6 cifre';

  @override
  String get pinIncorrect => 'Codice errato. Riprova.';

  @override
  String get pinIncomplet => 'Il codice ha 6 cifre.';

  @override
  String get pinRaz => 'Svuota';

  @override
  String get pinEffacer => 'Cancella l\'ultima cifra';

  @override
  String pinSaisi(int remplis, int total) {
    return '$remplis cifre inserite su $total';
  }

  @override
  String get deverrouillageActif => 'Sblocco offline attivo';

  @override
  String get donneesSurAppareil => 'Dati protetti sul dispositivo';

  @override
  String donneesSynchroniseesLe(String date) {
    return 'Ultimo accesso online: $date';
  }

  @override
  String get piedHorsLigne => 'ChantierSync · Modalità offline';

  @override
  String appareil(String id) {
    return 'Dispositivo $id';
  }

  @override
  String get retirerCompteTitre => 'Rimuovere questo account dal dispositivo?';

  @override
  String get retirerCompteTexte =>
      'I dati salvati su questo dispositivo saranno cancellati. Per tornare servirà un accesso online.';

  @override
  String get retirerCompteAction => 'Rimuovi l\'account';

  @override
  String retirerCompteAlerte(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other:
          'Attenzione: $n inserimenti non sono ancora stati inviati e andranno persi.',
      one:
          'Attenzione: 1 inserimento non è ancora stato inviato e andrà perso.',
    );
    return '$_temp0';
  }

  @override
  String get connexionAccroche => 'Il cantiere in tasca, anche senza rete.';

  @override
  String get identifiant => 'Nome utente';

  @override
  String get motDePasse => 'Password';

  @override
  String get afficherMotDePasse => 'Mostra la password';

  @override
  String get masquerMotDePasse => 'Nascondi la password';

  @override
  String get connexionAide =>
      'L\'accesso online serve una sola volta, poi si entra con il codice PIN.';

  @override
  String get comptesDemoTitre => 'Account dimostrativi';

  @override
  String get comptesDemoAide =>
      'Visibili solo perché i dati sono simulati. Tocca un profilo per compilare il modulo.';

  @override
  String get erreurIdentifiants => 'Nome utente o password errati.';

  @override
  String get erreurCompteInactif =>
      'Questo account è disattivato. Contatta l\'amministratore.';

  @override
  String erreurVerrouille(int secondes) {
    String _temp0 = intl.Intl.pluralLogic(
      secondes,
      locale: localeName,
      other: 'Account bloccato. Riprova tra $secondes secondi.',
      one: 'Account bloccato. Riprova tra 1 secondo.',
      zero: 'Account temporaneamente bloccato dopo vari tentativi falliti.',
    );
    return '$_temp0';
  }

  @override
  String get erreurSansAccesTerrain =>
      'Questo account non ha accesso di cantiere sull\'app mobile.';

  @override
  String get infoSessionRevoquee =>
      'L\'account è stato rimosso da questo dispositivo.';

  @override
  String get infoSessionExpiree =>
      'Più di 14 giorni senza accesso online: accedi di nuovo per continuare.';

  @override
  String get erreurDonneesInaccessibles =>
      'Impossibile aprire i dati del dispositivo.';

  @override
  String get erreurConnexionImpossible =>
      'Connessione impossibile. Controlla la rete e riprova.';

  @override
  String get definirCodeTitre => 'Imposta il mio codice';

  @override
  String get definirCodeSousTitre => 'Per aprire l\'app senza rete';

  @override
  String get choisirCode => 'Scegli un codice';

  @override
  String get choisirCodeAide => '6 cifre che conoscerai solo tu.';

  @override
  String get confirmerCode => 'Conferma il codice';

  @override
  String get confirmerCodeAide => 'Inserisci di nuovo lo stesso codice.';

  @override
  String get codesDifferents => 'I due codici non coincidono. Ricomincia.';

  @override
  String get synchroAJour => 'Dati aggiornati';

  @override
  String synchroEnAttente(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n elementi in attesa di invio',
      one: '1 elemento in attesa di invio',
    );
    return '$_temp0';
  }

  @override
  String get synchroTitre => 'Sincronizzazione';

  @override
  String get synchroExplication =>
      'I tuoi inserimenti sono salvati sul dispositivo e partono appena torna la connessione.';

  @override
  String get fileAttenteTitre => 'Coda di invio';

  @override
  String get fileVideTitre => 'Niente da inviare';

  @override
  String get fileVideTexte =>
      'Gli inserimenti fatti senza rete compariranno qui in attesa dell\'invio.';

  @override
  String get etatEnAttenteEnvoi => 'In attesa';

  @override
  String get etatEnvoye => 'Inviato';

  @override
  String get signatureTitre => 'Firma con il codice PIN';

  @override
  String get signatureAide => 'Il tuo codice conferma la decisione.';

  @override
  String get moduleEnPreparation => 'Quest\'area è in fase di allestimento.';

  @override
  String get profilLangue => 'Lingua';

  @override
  String get profilTheme => 'Aspetto';

  @override
  String get themeSysteme => 'Automatico';

  @override
  String get themeClair => 'Chiaro';

  @override
  String get themeSombre => 'Scuro';

  @override
  String get profilSynchroAide => 'Coda e stato degli invii';

  @override
  String get profilVerrouiller => 'Blocca';

  @override
  String get profilVerrouillerAide => 'Torna alla schermata del codice PIN';

  @override
  String get profilRetirerAide => 'Cancella i dati di questo dispositivo';

  @override
  String profilAPropos(String appareil) {
    return 'Schiavone Group · Italia Construction\nDispositivo $appareil · versione 1.0';
  }
}
