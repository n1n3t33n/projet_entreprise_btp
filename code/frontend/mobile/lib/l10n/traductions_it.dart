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

  @override
  String get niveauVide => 'Vuoto';

  @override
  String get niveauCritique => 'Critico';

  @override
  String get niveauMini => 'Minimo';

  @override
  String get niveauPlein => 'Pieno';

  @override
  String get stockNegatif => 'Giacenza negativa';

  @override
  String get stockNegatifExplication =>
      'La giacenza è negativa: anomalia da correggere con un inventario.';

  @override
  String get jaugeCapacite => 'Capacità';

  @override
  String get typeReception => 'Ricevimento';

  @override
  String get typeSortie => 'Uscita';

  @override
  String get typeRetour => 'Reso';

  @override
  String get typePerte => 'Perdita o rottura';

  @override
  String get typeAjustement => 'Rettifica d\'inventario';

  @override
  String get statutEnregistre => 'Registrato';

  @override
  String get statutAValider => 'Da validare';

  @override
  String get statutValide => 'Validato';

  @override
  String get statutRejete => 'Rifiutato';

  @override
  String get aLInstant => 'adesso';

  @override
  String ilYAMinutes(int n) {
    return '$n min fa';
  }

  @override
  String ilYAHeures(int n) {
    return '$n h fa';
  }

  @override
  String get aujourdhui => 'Oggi';

  @override
  String get hier => 'Ieri';

  @override
  String get choisirArticleTitre => 'Scegli un articolo';

  @override
  String get rechercherArticle => 'Cerca un articolo, un codice…';

  @override
  String get aucunResultat => 'Nessun articolo trovato';

  @override
  String get aucunResultatAide => 'Modifica la ricerca o il filtro.';

  @override
  String stockActuel(String quantite) {
    return 'giacenza attuale: $quantite';
  }

  @override
  String get sortieTitre => 'Uscita rapida';

  @override
  String get sortieAide => 'Consegnare materiale a una squadra';

  @override
  String get receptionTitre => 'Ricevimento';

  @override
  String get receptionAide => 'Registrare una bolla di consegna';

  @override
  String get retourTitre => 'Reso, rottura o perdita';

  @override
  String get retourAide => 'Dichiarare un\'eccedenza o materiale danneggiato';

  @override
  String get retourCourt => 'Reso / perdita';

  @override
  String get saisieSousTitre => 'Salvato sul dispositivo';

  @override
  String get saisieArticle => 'Articolo';

  @override
  String get saisieQuantite => 'Quantità';

  @override
  String get saisieMention => 'Invio automatico al ritorno della rete.';

  @override
  String get saisieIncomplete => 'Completa i campi obbligatori per confermare.';

  @override
  String toutLeStock(String quantite) {
    return 'Tutta la giacenza ($quantite)';
  }

  @override
  String get stockProjete => 'Giacenza dopo l\'inserimento';

  @override
  String get sortieDestination => 'Destinazione';

  @override
  String get sortieLogement => 'Alloggio o zona di posa';

  @override
  String get sortieCorpsEtat => 'Categoria di lavoro';

  @override
  String get sortieBeneficiaire => 'Squadra destinataria';

  @override
  String get facultatif => 'Facoltativo';

  @override
  String get receptionTracabilite => 'Bolla e fornitore';

  @override
  String get receptionBon => 'N. di bolla o di container';

  @override
  String get receptionBonExemple => 'Es. BL-2026-0589';

  @override
  String get receptionFournisseur => 'Fornitore';

  @override
  String get receptionEtat => 'Stato della consegna';

  @override
  String get receptionConforme => 'Conforme';

  @override
  String get receptionReserves => 'Con riserva';

  @override
  String get observations => 'Osservazioni';

  @override
  String get receptionObservationsExemple =>
      'Es. due sacchi strappati allo scarico';

  @override
  String get retourNature => 'Tipo di dichiarazione';

  @override
  String get natureRetour => 'Reso al magazzino';

  @override
  String get natureRetourDetail => 'Eccedenza rimessa a magazzino';

  @override
  String get natureCasse => 'Rottura o avaria';

  @override
  String get natureCasseDetail => 'Materiale danneggiato, inutilizzabile';

  @override
  String get naturePerte => 'Perdita';

  @override
  String get naturePerteDetail => 'Materiale mancante, introvabile';

  @override
  String get retourMotif => 'Motivo';

  @override
  String get retourMotifAide => 'Scegli un motivo';

  @override
  String get retourObservationsExemple =>
      'Es. bancale rimasto sotto la pioggia';

  @override
  String get motifSurplus => 'Eccedenza di cantiere';

  @override
  String get motifErreurMetre => 'Errore di computo';

  @override
  String get motifHumidite => 'Sacco strappato o umidità';

  @override
  String get motifChoc => 'Urto o caduta';

  @override
  String get motifIntrouvable => 'Introvabile al conteggio';

  @override
  String get motifAutre => 'Altro';

  @override
  String validerSortie(String quantite) {
    return 'Conferma l\'uscita ($quantite)';
  }

  @override
  String enregistrerReception(String quantite) {
    return 'Registra il ricevimento ($quantite)';
  }

  @override
  String validerDeclaration(String quantite) {
    return 'Conferma la dichiarazione ($quantite)';
  }

  @override
  String get mouvementEnregistre => 'Movimento salvato sul dispositivo.';

  @override
  String get controleOk =>
      'Giacenza sufficiente: l\'articolo resta sopra la soglia.';

  @override
  String avertissementSeuil(String reste, String seuil) {
    return 'Giacenza residua $reste, sotto la soglia minima di $seuil.';
  }

  @override
  String get avertissementNegatif =>
      'Questo inserimento rende negativa la giacenza. Sarà segnalato come anomalia.';

  @override
  String get registreTitre => 'Registro di magazzino';

  @override
  String get registreSousTitre => 'Quantità note al dispositivo';

  @override
  String get references => 'articoli';

  @override
  String get nouveauMouvement => 'Nuovo movimento';

  @override
  String get filtreTous => 'Tutti';

  @override
  String get filtreSousSeuil => 'Sotto soglia';

  @override
  String get filtreSorties => 'Uscite';

  @override
  String get filtreEntrees => 'Entrate';

  @override
  String seuilMini(String seuil) {
    return 'Soglia minima: $seuil';
  }

  @override
  String seuilMiniEcart(String seuil, String ecart) {
    return 'Soglia minima: $seuil ($ecart)';
  }

  @override
  String stockConforme(String seuil) {
    return 'Giacenza conforme (minimo: $seuil)';
  }

  @override
  String get ficheArticleTitre => 'Scheda articolo';

  @override
  String disponibles(String unite) {
    return '$unite a magazzino';
  }

  @override
  String get mouvementsRecents => 'Movimenti recenti';

  @override
  String get journalComplet => 'Registro completo';

  @override
  String get aucunMouvement => 'Nessun movimento';

  @override
  String get aucunMouvementAide =>
      'Uscite, ricevimenti e resi compariranno qui.';

  @override
  String get codeBarres => 'Codice a barre';

  @override
  String get journalTitre => 'Registro dei movimenti';

  @override
  String get journalSousTitre => 'Entrate e uscite del magazzino';

  @override
  String get journalRecherche => 'Cerca una bolla, un articolo, una persona…';

  @override
  String get mouvementsDuJour => 'movimenti di oggi';

  @override
  String get entreesDuJour => 'entrate di oggi';

  @override
  String get journalNonModifiable =>
      'Registro con data e ora, non modificabile';

  @override
  String get validationTitre => 'Validazioni';

  @override
  String get validationSousTitre => 'Uscite di magazzino e avvisi';

  @override
  String get ongletDemandes => 'Richieste';

  @override
  String get ongletAlertes => 'Avvisi di soglia';

  @override
  String get aucuneDemande => 'Nessuna uscita da validare';

  @override
  String get aucuneDemandeAide =>
      'Le uscite inserite dai magazzinieri compariranno qui.';

  @override
  String get aucuneAlerte => 'Nessun avviso';

  @override
  String get aucuneAlerteAide => 'Tutti gli articoli sono sopra la soglia.';

  @override
  String get materiau => 'Materiale';

  @override
  String get demandeur => 'Inserito da';

  @override
  String get affectation => 'Destinazione';

  @override
  String get rejeter => 'Rifiuta';

  @override
  String get approuver => 'Approva';

  @override
  String signatureSortie(String numero, String quantite) {
    return 'Approvare l\'uscita $numero ($quantite).';
  }

  @override
  String get sortieApprouvee => 'Uscita approvata.';

  @override
  String get sortieRefusee =>
      'Uscita rifiutata: la quantità torna a magazzino.';

  @override
  String get separationFonctions =>
      'Hai inserito questa operazione: deve validarla un\'altra persona.';

  @override
  String get stockRestant => 'Giacenza residua:';

  @override
  String get inventaireTitre => 'Inventario rotativo';

  @override
  String get inventaireEnCours => 'In corso';

  @override
  String inventaireProgression(int faits, int total) {
    String _temp0 = intl.Intl.pluralLogic(
      faits,
      locale: localeName,
      other: '$faits articoli contati',
      one: '1 articolo contato',
    );
    return '$_temp0 su $total';
  }

  @override
  String get articleEnControle => 'Articolo da contare';

  @override
  String get stockTheorique => 'Giacenza attesa';

  @override
  String get quantiteComptee => 'Quantità contata';

  @override
  String ecartDetecte(String ecart) {
    return 'Differenza rilevata: $ecart. Giustificazione obbligatoria.';
  }

  @override
  String get ecartChutes => 'Sfridi di taglio';

  @override
  String get ecartRebut => 'Materiale di scarto';

  @override
  String get ecartNonDeclare => 'Movimento non dichiarato';

  @override
  String get ecartRecompter => 'Conteggio da rifare';

  @override
  String get justificationObligatoire =>
      'Scegli una giustificazione per la differenza.';

  @override
  String validerArticle(String quantite) {
    return 'Conferma $quantite e passa al successivo';
  }

  @override
  String get soumettreInventaire => 'Invia l\'inventario alla validazione';

  @override
  String get inventaireSoumis => 'Inventario inviato per la validazione.';

  @override
  String get validerInventaire => 'Valida l\'inventario';

  @override
  String get inventaireValide =>
      'Inventario validato: la giacenza è stata rettificata.';

  @override
  String get inventaireRegle =>
      'La giacenza viene rettificata solo dopo questa validazione.';

  @override
  String signatureInventaire(String id, int n) {
    return 'Validare l\'inventario $id e rettificare la giacenza ($n differenze).';
  }

  @override
  String get inventaireEnAttenteValidation =>
      'Conteggio terminato. L\'inventario attende la validazione del responsabile di magazzino.';

  @override
  String get inventaireArticles => 'Articoli della zona';

  @override
  String get inventaireAValider => 'Inventario da validare';

  @override
  String inventaireEcarts(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n differenze da esaminare',
      one: '1 differenza da esaminare',
      zero: 'Nessuna differenza',
    );
    return '$_temp0';
  }

  @override
  String get aCompter => 'Da contare';

  @override
  String get conforme => 'Conforme';

  @override
  String get alertesPriorites => 'Avvisi e priorità';

  @override
  String voirToutesAlertes(int n) {
    return 'Vedi tutti i $n avvisi';
  }

  @override
  String get stockMagasin => 'Giacenze di magazzino';

  @override
  String get sousSeuil => 'sotto soglia';

  @override
  String get consulterStock => 'Consulta il magazzino';

  @override
  String get consulterRegistre => 'Apri il registro';

  @override
  String get raccourcis => 'Scorciatoie';

  @override
  String get reprendreComptage => 'Riprendi il conteggio';

  @override
  String get suivreInventaire => 'Segui il conteggio';

  @override
  String get mouvements24h => 'mov. in 24 h';

  @override
  String get sortiesAValider => 'Uscite da validare';

  @override
  String nombreDemandes(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n richieste',
      one: '1 richiesta',
      zero: 'Aggiornato',
    );
    return '$_temp0';
  }

  @override
  String examinerSorties(int n) {
    return 'Esamina le $n uscite';
  }

  @override
  String get etapeAFaire => 'Da fare';

  @override
  String get etapeEnCours => 'In corso';

  @override
  String get etapeADeclaree => 'Da validare';

  @override
  String get etapeValidee => 'Validata';

  @override
  String get etapeBloquee => 'Bloccata';

  @override
  String get etapesFaites => 'completate';

  @override
  String get filtreToutes => 'Tutte';

  @override
  String get evDemarrage => 'Avvio';

  @override
  String get evPointage => 'Avanzamento';

  @override
  String get evPause => 'Pausa';

  @override
  String get evReprise => 'Ripresa';

  @override
  String get evBlocage => 'Blocco';

  @override
  String get evLeveeBlocage => 'Blocco rimosso';

  @override
  String get evFin => 'Fine dichiarata';

  @override
  String get evValidation => 'Validazione';

  @override
  String get evRejet => 'Ripresa richiesta';

  @override
  String get evReaffectation => 'Riassegnazione';

  @override
  String get blocageRupture => 'Mancanza di materiale';

  @override
  String get blocagePanne => 'Guasto di mezzi o attrezzi';

  @override
  String get blocageIntemperies => 'Maltempo';

  @override
  String get blocageNonConformite => 'Supporto non conforme';

  @override
  String get blocageAcces => 'Accesso al cantiere bloccato';

  @override
  String get graviteArret => 'Fermo totale';

  @override
  String get graviteRalenti => 'Rallentato';

  @override
  String get graviteAlerte => 'Solo avviso';

  @override
  String get retardDeuxHeures => '2 ore';

  @override
  String get retardDemiJournee => 'Mezza giornata';

  @override
  String get retardUnJour => 'Un giorno o più';

  @override
  String get ficheRouteTitre => 'Scheda di lavoro';

  @override
  String get progressionJour => 'Avanzamento di oggi';

  @override
  String etapesTerminees(int faits, int total) {
    return '$faits fasi completate su $total';
  }

  @override
  String get aucuneEtape => 'Nessuna fase';

  @override
  String get aucuneEtapeAide => 'Nessuna fase corrisponde per ora.';

  @override
  String etapeTitre(String id) {
    return 'Fase $id';
  }

  @override
  String get actionImpossible =>
      'Azione non possibile nello stato attuale della fase.';

  @override
  String get demarrerEtape => 'Avvia la fase';

  @override
  String validerPointage(String valeur) {
    return 'Salva l\'avanzamento ($valeur)';
  }

  @override
  String get pointageEnregistre => 'Avanzamento salvato sul dispositivo.';

  @override
  String get terminerEtape => 'Dichiara la fase completata';

  @override
  String get etapeDeclaree =>
      'Fase dichiarata completata: in attesa di validazione.';

  @override
  String get terminerMention => 'Un\'altra persona dovrà validare la fase.';

  @override
  String get terminerConditions =>
      'Per completare: quantità raggiunta e tutti i controlli spuntati.';

  @override
  String get leverBlocage => 'Rimuovi il blocco';

  @override
  String get journalEtapeTitre => 'Registro della fase';

  @override
  String get journalEtapeSousTitre => 'Attività con data e ora';

  @override
  String get localisation => 'Posizione';

  @override
  String get pointageActif => 'RILEVAZIONE IN CORSO';

  @override
  String get pointageArrete => 'RILEVAZIONE IN PAUSA';

  @override
  String get mettreEnPause => 'Metti in pausa';

  @override
  String get reprendre => 'Riprendi';

  @override
  String get avancementMetre => 'Avanzamento delle quantità';

  @override
  String cible(String valeur) {
    return 'Obiettivo: $valeur';
  }

  @override
  String surCible(String valeur) {
    return 'su $valeur';
  }

  @override
  String get solde => 'Tutto il resto';

  @override
  String get gammeSecurite => 'Procedura e sicurezza';

  @override
  String get declarerBlocage => 'Segnala un blocco';

  @override
  String get reaffecterEtape => 'Riassegna a un\'altra squadra';

  @override
  String get blocageTitre => 'Segnala un blocco';

  @override
  String get blocageMention =>
      'L\'avviso parte verso l\'ufficio appena torna la connessione.';

  @override
  String get transmettreBlocage => 'Invia l\'avviso di blocco';

  @override
  String get blocageTransmis => 'Blocco registrato: la fase è ferma.';

  @override
  String get blocageNature => 'Tipo di blocco';

  @override
  String get blocageArticle => 'Indica l\'articolo mancante';

  @override
  String get blocageGravite => 'Gravità';

  @override
  String get blocageRetard => 'Ritardo stimato';

  @override
  String get blocageObservationsExemple =>
      'Es. consegna del cemento in ritardo di 3 h';

  @override
  String get controlesTitre => 'Controlli e accettazione';

  @override
  String get controlesSousTitre => 'Fasi dichiarate completate';

  @override
  String signatureEtape(String id, String libelle) {
    return 'Validare la fase $id: $libelle.';
  }

  @override
  String get etapeValideeMessage => 'Fase validata.';

  @override
  String get etapeRefuseeMessage =>
      'Ripresa richiesta: la fase torna in corso.';

  @override
  String get aucunControle => 'Nessuna fase da validare';

  @override
  String get aucunControleAide =>
      'Le fasi dichiarate completate compariranno qui.';

  @override
  String declarePar(String nom) {
    return 'Dichiarata completata da $nom';
  }

  @override
  String get validerEtape => 'Valida';

  @override
  String get reaffectationTitre => 'Riassegnazione';

  @override
  String get reaffectationMention =>
      'La nuova squadra vedrà la fase sulla sua scheda.';

  @override
  String get confirmerReaffectation => 'Conferma la riassegnazione';

  @override
  String reaffectationFaite(String equipe) {
    return 'Fase affidata a $equipe.';
  }

  @override
  String get reaffectationMotif => 'Motivo';

  @override
  String get motifRetardPlanning => 'Ritardo di programma';

  @override
  String get motifAbsence => 'Assenza di operai';

  @override
  String get motifCompetence => 'Competenza richiesta';

  @override
  String get motifSurcroit => 'Picco di attività';

  @override
  String get reaffectationEquipe => 'Nuova squadra';

  @override
  String equipeDetail(String chef, int n) {
    return 'Capo: $chef · $n operai';
  }

  @override
  String get chargeActuelle => 'Carico';

  @override
  String get reaffectationConsigne => 'Nota di consegna';

  @override
  String get reaffectationConsigneExemple =>
      'Es. casseri pronti, attendere la consegna del calcestruzzo';

  @override
  String get dureePointee => 'tempo rilevato';

  @override
  String get evenementsTraces => 'eventi registrati';

  @override
  String get aucunEvenement => 'Nessuna attività';

  @override
  String get aucunEvenementAide =>
      'Avvii, avanzamenti e validazioni compariranno qui.';

  @override
  String pourcentRealise(int n) {
    return '$n% completato';
  }

  @override
  String get ouvrirFicheRoute => 'Apri la scheda di lavoro';

  @override
  String get maFicheDuJour => 'La mia scheda di oggi';

  @override
  String get pointageRapide => 'Avanzamento rapido';

  @override
  String get prochainesEtapes => 'Prossime fasi';

  @override
  String get aValiderPriorite => 'Da validare per primo';

  @override
  String nombreActions(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n azioni',
      one: '1 azione',
      zero: 'Aggiornato',
    );
    return '$_temp0';
  }

  @override
  String get sortiesAValiderDetail => 'Bolle di materiale del magazzino';

  @override
  String get etapesAControler => 'Fasi da controllare';

  @override
  String get etapesAControlerDetail => 'Lavori dichiarati completati';

  @override
  String nombreEtapes(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n fasi',
      one: '1 fase',
      zero: 'Nessuna fase',
    );
    return '$_temp0';
  }

  @override
  String get blocagesPrioritaires => 'Blocchi in corso';

  @override
  String get aucunBlocage => 'Nessuna fase bloccata.';

  @override
  String get supervisionTravaux => 'Supervisione lavori e conformità';

  @override
  String get visasTechniques => 'Approvazioni tecniche';

  @override
  String get examinerEtapes => 'Esamina le fasi';

  @override
  String get syntheseChantier => 'Sintesi per categoria di lavoro';

  @override
  String etapesValideesSur(int faits, int total) {
    return '$faits fasi validate su $total';
  }

  @override
  String get outilsPosteFixe => 'Strumenti completi da postazione fissa';

  @override
  String get outilsPosteFixeAide =>
      'Pianificazioni, squadre ed esportazioni si gestiscono dalla postazione web.';
}
