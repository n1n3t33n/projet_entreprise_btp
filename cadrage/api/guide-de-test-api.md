# Guide de test de l'API ChantierSync

Ce guide permet de tester **toutes les routes** de l'API du serveur
ChantierSync, une par une, sur un poste Windows. Chaque étape dit ce qu'elle
vérifie, donne la commande à coller dans PowerShell et le résultat attendu.

À la fin, un bilan affiche le nombre de vérifications et la liste des
écarts. Un tableau (§ 14) relie chacune des 95 opérations du contrat à
l'étape qui la teste.

## Sommaire

0. [Avant de commencer](#0-avant-de-commencer)
1. [Préparer la console](#1-préparer-la-console)
2. [Santé, session et contrôles transverses](#2-santé-session-et-contrôles-transverses)
3. [Comptes, droits et journal d'audit](#3-comptes-droits-et-journal-daudit)
4. [Référentiels](#4-référentiels)
5. [Paramétrage, corps d'état et gammes](#5-paramétrage-corps-détat-et-gammes)
6. [Stock : mouvements et validations](#6-stock--mouvements-et-validations)
7. [Stock : seuils, alertes et inventaire](#7-stock--seuils-alertes-et-inventaire)
8. [Avancement des travaux et fiches de route](#8-avancement-des-travaux-et-fiches-de-route)
9. [Application mobile : synchronisation et appareils](#9-application-mobile--synchronisation-et-appareils)
10. [Notifications](#10-notifications)
11. [Pilotage](#11-pilotage)
12. [Espace acquéreur](#12-espace-acquéreur)
13. [Exploitation, déconnexion et limitation des tentatives](#13-exploitation-déconnexion-et-limitation-des-tentatives)
14. [Bilan et tableau de couverture](#14-bilan-et-tableau-de-couverture)

---

## 0. Avant de commencer

### Ce qu'il faut

- Le serveur installé selon `code/backend/README.md` : PostgreSQL 16,
  environnement virtuel, fichier `.env` rempli, migrations passées.
- **Windows PowerShell** (celui livré avec Windows suffit). Aucun autre
  outil n'est nécessaire.
- Le mot de passe de démonstration : la valeur de `DEMO_MOT_DE_PASSE` dans
  `code/backend/.env`. Il ne s'affiche jamais à l'écran pendant le test.

### Sur quelle base tester

Le test **écrit** dans la base : il crée des articles, une zone, des
mouvements de stock, un inventaire, valide des étapes… Les registres de
mouvements et d'événements sont immuables : ce qui est écrit ne s'efface
pas. Partir de la démonstration fraîchement chargée garantit les résultats
attendus de ce guide.

Deux possibilités :

- **Simple** : la base de développement. Recharger la démonstration avant
  le test (`python manage.py charger_demo`). Les données de test restent
  ensuite dans la base, toutes repérables par le code `TEST-…`.
- **Propre** (recommandée avant une soutenance) : une base dédiée, détruite
  après le test. En superutilisateur PostgreSQL :

  ```powershell
  & "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -h 127.0.0.1 -c "CREATE DATABASE chantiersync_essai OWNER chantiersync_proprietaire"
  ```

  Puis, dans le dossier `code/backend`, avec l'environnement virtuel activé,
  en désignant cette base pour la session PowerShell en cours seulement :

  ```powershell
  $env:DB_NOM = "chantiersync_essai"
  python manage.py migrate --database migration
  python manage.py charger_demo
  ```

  Après le test : arrêter le serveur, puis
  `psql -U postgres -h 127.0.0.1 -c "DROP DATABASE chantiersync_essai"`.

### Démarrer le serveur

Dans une **première** fenêtre PowerShell, dans `code/backend` (avec
`$env:DB_NOM` si la base dédiée est choisie) :

```powershell
..\venv\Scripts\Activate.ps1
python manage.py runserver 8000
```

Laisser cette fenêtre ouverte : elle affiche une ligne par requête reçue.
Toutes les commandes qui suivent se tapent dans une **seconde** fenêtre
PowerShell.

### Comptes de démonstration

Tous ont le même mot de passe (`DEMO_MOT_DE_PASSE`).

| Variable du guide | Identifiant | Rôle | Ce qu'il peut faire |
| --- | --- | --- | --- |
| `$Admin` | `y.bamba` | ADMINISTRATEUR | tout, dont comptes, droits, appareils, audit |
| `$Direction` | `a.kouassi` | DIRECTION | lectures, audit, rapport hebdomadaire |
| `$Commercial` | `s.traore` | COMMERCIAL | lectures de référentiels et d'avancement |
| `$Acquereuse` | `m.diallo` | ACQUEREUR | son logement (A01) et ses notifications |
| `$Magasinier` | `magasinier` | MAGASINIER | saisir des mouvements, compter un inventaire |
| `$Gestionnaire` | `gestionnaire` | GESTIONNAIRE_STOCK | valider sorties et inventaires, seuils, import |
| `$Technicien` | `technicien` | TECHNICIEN | déclarer et bloquer des étapes |
| `$Chef` | `chef` | CHEF_CHANTIER | valider des étapes, affecter les fiches de route |
| `$Responsable` | `responsable` | RESPONSABLE_TECHNIQUE | gammes, corps d'état, paramètres, règles |

### Lire un résultat

Chaque appel affiche une ligne :

```
[OK]     201 POST /api/mouvements
[ÉCART]  POST /api/mouvements : attendu 201, reçu 403 ACCES_REFUSE (Vous n'avez pas le droit…)
```

- `[OK]` : le serveur a répondu exactement ce qui est attendu, y compris
  quand c'est un **refus voulu** (un magasinier qui tente de valider sa
  propre sortie doit recevoir `403`).
- `[ÉCART]` : le résultat diffère. Noter la ligne, le motif et le message ;
  la fenêtre du serveur donne le détail.

Les codes à connaître : `200` lu ou modifié, `201` créé, `204` modifié sans
contenu, `400` données invalides, `401` non connecté, `403` interdit,
`404` introuvable ou hors de son périmètre, `405` méthode refusée, `409`
conflit avec l'état (déjà fait, déjà annulé…), `429` trop de tentatives.

---

## 1. Préparer la console

Coller ce bloc **en entier** dans la seconde fenêtre. Il définit l'adresse
du serveur, demande le mot de passe sans l'afficher et crée trois outils :

- `Invoke-Api` envoie une requête, compare le code reçu à celui attendu et
  rend le contenu de la réponse (le corps d'un refus reste lisible dans
  `$DerniereErreur`, les en-têtes de la réponse dans `$DernieresEntetes`) ;
- `Connect-Compte` connecte un compte et rend son jeton ;
- `Show-Bilan` résume le test.

```powershell
$Base = "http://127.0.0.1:8000"
$Bilan = New-Object System.Collections.ArrayList
$Suffixe = Get-Random -Minimum 10000 -Maximum 99999   # rend les codes de test uniques
$secret = Read-Host "Mot de passe de démonstration (DEMO_MOT_DE_PASSE)" -AsSecureString
$MotDePasse = [System.Net.NetworkCredential]::new("", $secret).Password

function Invoke-Api {
    param(
        [Parameter(Mandatory = $true, Position = 0)][string]$Methode,
        [Parameter(Mandatory = $true, Position = 1)][string]$Chemin,
        [Parameter(Position = 2)]$Corps = $null,
        [string]$Jeton = "",
        [int]$Attendu = 200,
        [string]$Motif = "",
        [hashtable]$Entetes = @{},
        [switch]$HorsBilan
    )
    # Requête HTTP brute : le code et le corps sont lus même en cas d'erreur.
    $requete = [System.Net.HttpWebRequest]::Create("$Base$Chemin")
    $requete.Method = $Methode
    if ($Jeton) { $requete.Headers["Authorization"] = "Bearer $Jeton" }
    foreach ($cle in $Entetes.Keys) { $requete.Headers[$cle] = $Entetes[$cle] }
    if ($null -ne $Corps) {
        $octets = [System.Text.Encoding]::UTF8.GetBytes((ConvertTo-Json -InputObject $Corps -Depth 10 -Compress))
        $requete.ContentType = "application/json; charset=utf-8"
        $flux = $requete.GetRequestStream(); $flux.Write($octets, 0, $octets.Length); $flux.Close()
    } elseif ($Methode -ne "GET") { $requete.ContentLength = 0 }
    try { $reponse = $requete.GetResponse() }
    catch [System.Net.WebException] {
        $reponse = $_.Exception.Response
        if ($null -eq $reponse) { throw "Serveur injoignable sur $Base : est-il démarré ?" }
    }
    $code = [int]$reponse.StatusCode
    $type = [string]$reponse.ContentType
    $script:DernieresEntetes = $reponse.Headers
    $lecteur = New-Object System.IO.StreamReader($reponse.GetResponseStream(), [System.Text.Encoding]::UTF8)
    $texte = $lecteur.ReadToEnd(); $lecteur.Close(); $reponse.Close()
    $donnees = $texte
    if ($texte -and $type -like "application/json*") { $donnees = ConvertFrom-Json -InputObject $texte }
    # Comparaison avec le résultat attendu, puis affichage et bilan.
    $motifRecu = ""
    if ($code -ge 400 -and $donnees -isnot [string]) { $motifRecu = [string]$donnees.motif }
    $conforme = ($code -eq $Attendu) -and (-not $Motif -or $motifRecu -eq $Motif)
    $libelle = "$Methode $($Chemin.Split('?')[0])"
    if ($conforme) {
        Write-Host "[OK]     $code $libelle $motifRecu" -ForegroundColor Green
    } else {
        $attenduTexte = "$Attendu $Motif".Trim()
        $message = ""
        if ($donnees -isnot [string] -and $donnees.message) { $message = "($($donnees.message))" }
        Write-Host "[ÉCART]  $libelle : attendu $attenduTexte, reçu $code $motifRecu $message" -ForegroundColor Red
    }
    if (-not $HorsBilan) { [void]$Bilan.Add([pscustomobject]@{ Requete = $libelle; Attendu = "$Attendu $Motif".Trim(); Recu = "$code $motifRecu".Trim(); Conforme = $conforme }) }
    $script:DernierCode = $code
    # Un refus ne rend rien : son motif est déjà affiché, son corps est
    # gardé dans $DerniereErreur.
    if ($code -ge 400) { $script:DerniereErreur = $donnees; return }
    return $donnees
}

function Connect-Compte {
    param([Parameter(Mandatory = $true)][string]$Identifiant, [hashtable]$Appareil = $null)
    $corps = @{ identifiant = $Identifiant; mot_de_passe = $MotDePasse }
    if ($Appareil) { $corps.appareil = $Appareil }
    $session = Invoke-Api POST /api/auth/connexion $corps
    return $session.jeton
}

function Show-Bilan {
    $ecarts = @($Bilan | Where-Object { -not $_.Conforme })
    Write-Host ""
    Write-Host "$($Bilan.Count) vérifications, $($ecarts.Count) écart(s)." -ForegroundColor Cyan
    if ($ecarts.Count -gt 0) { $ecarts | Format-Table Requete, Attendu, Recu -AutoSize }
}
```

Si la console refuse un bloc (« l'exécution de scripts est désactivée »),
ce n'est pas le cas ici : rien n'est enregistré en fichier, tout est collé.

---

## 2. Santé, session et contrôles transverses

### 2.1 Le serveur répond

Routes publiques, sans jeton : la vivacité (le processus tourne) et
l'aptitude (la base répond et les migrations sont à jour).

```powershell
Invoke-Api GET /api/sante/vivacite | Out-Null
(Invoke-Api GET /api/sante/aptitude).verifications | Format-List
```

Attendu : `[OK] 200` deux fois ; l'aptitude affiche
`base_de_donnees : OK` et `migrations : OK`.

### 2.2 Connexion de tous les comptes

Une connexion par rôle ; chaque jeton est rangé dans une variable.

```powershell
$Admin        = Connect-Compte y.bamba
$Direction    = Connect-Compte a.kouassi
$Commercial   = Connect-Compte s.traore
$Acquereuse   = Connect-Compte m.diallo
$Magasinier   = Connect-Compte magasinier
$Gestionnaire = Connect-Compte gestionnaire
$Technicien   = Connect-Compte technicien
$Chef         = Connect-Compte chef
$Responsable  = Connect-Compte responsable
```

Attendu : neuf `[OK] 200 POST /api/auth/connexion`.

### 2.3 Mauvais mot de passe

```powershell
Invoke-Api POST /api/auth/connexion @{ identifiant = "magasinier"; mot_de_passe = "faux-mot-de-passe" } -Attendu 401 -Motif IDENTIFIANTS
```

Attendu : `[OK] 401 … IDENTIFIANTS`. Le message ne dit pas si c'est
l'identifiant ou le mot de passe qui est faux.

### 2.4 La session ouverte

```powershell
$Moi = Invoke-Api GET /api/auth/moi -Jeton $Magasinier
$Moi.utilisateur | Format-List identifiant, prenom, nom, role_code_role, libelle_perimetre
$DernieresEntetes["X-Horodatage-Serveur"]
```

Attendu : `[OK] 200`, le compte « magasinier » (rôle MAGASINIER, périmètre
« Magasin central de Grand-Bassam »), puis l'heure du serveur, que le
téléphone garde pour son verrou de 14 jours.

### 2.5 Requêtes refusées sans jeton ou avec un faux jeton

```powershell
Invoke-Api GET /api/auth/moi -Attendu 401 -Motif NON_AUTHENTIFIE
Invoke-Api GET /api/auth/moi -Jeton "jeton-invente" -Attendu 401 -Motif JETON_INVALIDE
```

### 2.6 Routes inconnues, méthodes refusées, corrélation

```powershell
Invoke-Api GET /api/route-qui-n-existe-pas -Jeton $Admin -Attendu 404
Invoke-Api DELETE /api/referentiels/articles -Jeton $Admin -Attendu 405 -Motif METHODE_NON_AUTORISEE
$Correlation = [guid]::NewGuid().ToString()
Invoke-Api GET /api/auth/moi -Jeton $Admin -Entetes @{ "X-Request-ID" = $Correlation } | Out-Null
$DernieresEntetes["X-Request-ID"] -eq $Correlation
```

Attendu : `[OK] 404`, `[OK] 405`, `[OK] 200`, puis `True` : le serveur
renvoie l'identifiant de corrélation reçu (utile pour retrouver une requête
dans ses journaux).

---

## 3. Comptes, droits et journal d'audit

### 3.1 Lire les comptes, rôles, permissions et périmètres

```powershell
$Comptes = Invoke-Api GET /api/auth/comptes -Jeton $Admin
$Comptes | Format-Table identifiant, role_code_role, statut, libelle_perimetre -AutoSize
Invoke-Api GET /api/droits/roles -Jeton $Admin | Format-Table code_role, libelle -AutoSize
(Invoke-Api GET /api/droits/permissions -Jeton $Admin).Count
$Perimetres = Invoke-Api GET /api/auth/perimetres -Jeton $Admin
$Perimetres | Format-Table -AutoSize
$PerimetreMagasin = ($Perimetres | Where-Object libelle -like "Magasin*").id_perimetre
```

Attendu : quatre `[OK] 200` ; 14 comptes (10 avec un rôle, 4 membres
d'équipe sans accès), 9 rôles, 86 permissions, 3 périmètres.

### 3.2 Un non-administrateur ne voit pas les comptes

```powershell
Invoke-Api GET /api/auth/comptes -Jeton $Magasinier -Attendu 403 -Motif ACCES_REFUSE
```

### 3.3 Créer un compte, puis le désactiver

```powershell
$NouveauCompte = @{
    identifiant = "test.$Suffixe"; prenom = "Essai"; nom = "Magasinier"; fonction = "Compte de test"
    statut = "ACTIF"; role_code_role = "MAGASINIER"; perimetre_id_perimetre = $PerimetreMagasin
    mot_de_passe = "Essai-$Suffixe-Chantier!"
}
$Compte = Invoke-Api POST /api/auth/comptes $NouveauCompte -Jeton $Admin -Attendu 201
$NouveauCompte.statut = "INACTIF"
Invoke-Api PUT "/api/auth/comptes/$($Compte.id_utilisateur)" $NouveauCompte -Jeton $Admin | Out-Null
Invoke-Api POST /api/auth/connexion @{ identifiant = "test.$Suffixe"; mot_de_passe = "Essai-$Suffixe-Chantier!" } -Attendu 403 -Motif COMPTE_INACTIF
```

Attendu : `201` à la création, `200` à la modification, puis la connexion
du compte désactivé refusée (`403 COMPTE_INACTIF`).

### 3.4 Rattachement d'un compte à un acquéreur

Seul un compte de rôle ACQUEREUR peut être rattaché à un acquéreur
(règle RG-D10). On réutilise l'acquéreur de Mariam Diallo.

```powershell
$IdAcquereur = ($Comptes | Where-Object identifiant -eq "m.diallo").acquereur_id_acquereur
$NouveauCompte.acquereur_id_acquereur = $IdAcquereur
Invoke-Api PUT "/api/auth/comptes/$($Compte.id_utilisateur)" $NouveauCompte -Jeton $Admin -Attendu 400 -Motif DONNEES_INVALIDES
$NouveauCompte.Remove("acquereur_id_acquereur")
```

Attendu : `400` : un compte magasinier ne peut pas être rattaché.

### 3.5 La matrice des droits

On relit la matrice puis on la renvoie telle quelle : le serveur la
remplace par elle-même (aucun changement réel) et le journalise.

```powershell
$Matrice = @(Invoke-Api GET /api/droits/accordes -Jeton $Admin)
$Matrice.Count
Invoke-Api PUT /api/droits/accordes @{ droits = $Matrice } -Jeton $Admin | Out-Null
Invoke-Api PUT /api/droits/accordes @{ droits = $Matrice } -Jeton $Gestionnaire -Attendu 403
```

Attendu : `200` pour l'administrateur, `403` pour la gestionnaire.

### 3.6 Le journal d'audit

```powershell
Invoke-Api GET "/api/audit?limite=10" -Jeton $Admin | Format-Table horodatage, identifiant_utilisateur, action, resume -AutoSize
Invoke-Api GET "/api/audit?action=CONNEXION&limite=5" -Jeton $Direction | Out-Null
Invoke-Api GET /api/audit -Jeton $Magasinier -Attendu 403
```

Attendu : les dernières actions (connexions, création du compte, matrice
des droits…), lisibles par l'administrateur et la direction, refusées au
magasinier.

---

## 4. Référentiels

### 4.1 Lire les référentiels

```powershell
$Chantier = @(Invoke-Api GET /api/referentiels/chantiers -Jeton $Admin)[0]
$Arbo = Invoke-Api GET "/api/referentiels/chantiers/$($Chantier.id_chantier)/arborescence" -Jeton $Admin
$ZoneA = $Arbo.zones[0].zone
$A01 = ($Arbo.zones[0].logements | Where-Object numero -eq "A01").id_logement
$Articles = Invoke-Api GET /api/referentiels/articles -Jeton $Admin
$Ciment = ($Articles | Where-Object code -eq "A0001").id_article
$MagasinRef = @(Invoke-Api GET /api/referentiels/magasins -Jeton $Admin)[0]
Invoke-Api GET /api/referentiels/categories -Jeton $Commercial | Out-Null
Invoke-Api GET /api/referentiels/unites -Jeton $Commercial | Out-Null
Invoke-Api GET /api/referentiels/types-logement -Jeton $Commercial | Out-Null
Invoke-Api GET /api/types-mouvement -Jeton $Magasinier | Format-Table code_type_mouvement, sens, motif_obligatoire -AutoSize
Invoke-Api GET /api/motifs-blocage -Jeton $Technicien | Out-Null
Invoke-Api GET "/api/chantiers/$($Chantier.id_chantier)/logements" -Jeton $Commercial | Out-Null
```

Attendu : dix `[OK] 200`. Le chantier de Grand-Bassam, l'îlot A, 60
articles (le ciment est `A0001`), un magasin, 9 types de mouvement.

### 4.2 Article : création, modification, doublon, refus

```powershell
$Article = @{ code = "TEST-$Suffixe"; designation = "Article de test"; origine = "ACHAT"; unite_mesure_code_unite = "SAC"; categorie_article_code_categorie = "GO-CIM" }
$ArticleCree = Invoke-Api POST /api/referentiels/articles $Article -Jeton $Gestionnaire -Attendu 201
$Article.designation = "Article de test (modifié)"
Invoke-Api PUT "/api/referentiels/articles/$($ArticleCree.id_article)" $Article -Jeton $Gestionnaire | Out-Null
Invoke-Api POST /api/referentiels/articles $Article -Jeton $Gestionnaire -Attendu 400 -Motif DONNEES_INVALIDES
Invoke-Api POST /api/referentiels/articles @{ code = "X" } -Jeton $Gestionnaire -Attendu 400 -Motif DONNEES_INVALIDES
Invoke-Api POST /api/referentiels/articles $Article -Jeton $Magasinier -Attendu 403
```

Attendu : `201` puis `200` ; le même code une seconde fois et un article
incomplet sont refusés (`400`, avec `details` qui nomme le champ en cause) ;
le magasinier n'a pas le droit de créer (`403`).

### 4.3 Zone et logement

Un logement créé reçoit automatiquement les étapes de la gamme active de
son type.

```powershell
$Zone = @{ code = "TEST-$Suffixe"; nom = "Zone de test"; type_zone = "TRANCHE"; chantier_id_chantier = $Chantier.id_chantier }
$ZoneCreee = Invoke-Api POST /api/referentiels/zones $Zone -Jeton $Admin -Attendu 201
$Zone.nom = "Zone de test (modifiée)"
Invoke-Api PUT "/api/referentiels/zones/$($ZoneCreee.id_zone)" $Zone -Jeton $Admin | Out-Null
$Logement = @{ numero = "T$Suffixe"; statut = "A_VENIR"; zone_id_zone = $ZoneCreee.id_zone; type_logement_code_type = "VILLA3" }
$LogementCree = Invoke-Api POST /api/referentiels/logements $Logement -Jeton $Admin -Attendu 201
$Logement.date_livraison_prevue = "2027-06-30"
Invoke-Api PUT "/api/referentiels/logements/$($LogementCree.id_logement)" $Logement -Jeton $Admin | Out-Null
(Invoke-Api GET "/api/logements/$($LogementCree.id_logement)/etapes" -Jeton $Admin).Count
```

Attendu : `201`, `200`, `201`, `200`, `200`, puis `10` : les dix étapes de
la gamme « Villa 3 pièces ».

### 4.4 Magasin et chantier

```powershell
$Magasin = @{ code = "TEST-$Suffixe"; nom = "Magasin de test"; chantier_id_chantier = $Chantier.id_chantier }
$MagasinCree = Invoke-Api POST /api/referentiels/magasins $Magasin -Jeton $Admin -Attendu 201
$Magasin.actif = $false
Invoke-Api PUT "/api/referentiels/magasins/$($MagasinCree.id_magasin)" $Magasin -Jeton $Admin | Out-Null
$ChantierCorps = @{ code = $Chantier.code; nom = $Chantier.nom; programme = $Chantier.programme; date_debut = $Chantier.date_debut; statut = $Chantier.statut }
Invoke-Api PUT "/api/referentiels/chantiers/$($Chantier.id_chantier)" $ChantierCorps -Jeton $Admin | Out-Null
```

Attendu : `201`, `200`, `200` (le chantier est réécrit à l'identique).

### 4.5 Import CSV : analyse puis confirmation

L'analyse n'écrit rien ; la confirmation écrit les lignes valides.

```powershell
$Csv = "code;designation;unite`nTEST-$Suffixe-IMP;Article importé;SAC`nTEST-$Suffixe-ERR;Unité inconnue;XXX"
$Analyse = Invoke-Api POST /api/import/analyse @{ cible = "articles"; contenu = $Csv } -Jeton $Gestionnaire
$Analyse | ConvertTo-Json -Depth 5
Invoke-Api POST /api/import/confirmation @{ cible = "articles"; contenu = $Csv } -Jeton $Gestionnaire | ConvertTo-Json -Depth 5
Invoke-Api POST /api/import/analyse @{ cible = "articles"; contenu = "colonne_inconnue`n1" } -Jeton $Gestionnaire -Attendu 400
```

Attendu : l'analyse signale une ligne valide et une ligne en erreur (unité
inconnue) ; la confirmation crée l'article valide seulement ; un en-tête
inconnu est refusé (`400`, la liste des colonnes possibles est dans
`details`).

---

## 5. Paramétrage, corps d'état et gammes

### 5.1 Paramètres de chantier

```powershell
Invoke-Api GET "/api/parametrage/parametres?chantier=$($Chantier.id_chantier)" -Jeton $Responsable | Format-Table cle, valeur -AutoSize
$Parametre = @{ cle = "test_$Suffixe"; valeur = "1"; type_valeur = "ENTIER"; libelle = "Paramètre de test"; chantier_id_chantier = $Chantier.id_chantier }
$ParametreCree = Invoke-Api POST /api/parametrage/parametres $Parametre -Jeton $Responsable -Attendu 201
$Parametre.valeur = "2"
Invoke-Api PUT "/api/parametrage/parametres/$($ParametreCree.id_parametre)" $Parametre -Jeton $Responsable | Out-Null
$Parametre.valeur = "pas-un-nombre"
Invoke-Api PUT "/api/parametrage/parametres/$($ParametreCree.id_parametre)" $Parametre -Jeton $Responsable -Attendu 400
```

Attendu : `200`, `201`, `200`, puis `400` : la valeur ne correspond pas au
type `ENTIER`.

### 5.2 Règles de validation

La règle créée ici ne gêne pas la suite (seuil très élevé).

```powershell
Invoke-Api GET /api/parametrage/regles -Jeton $Responsable | Format-Table type_evenement, champ_teste, operateur, valeur_seuil -AutoSize
$Regle = @{ type_evenement = "MOUVEMENT_STOCK"; champ_teste = "quantite_base"; operateur = "SUPERIEUR_EGAL"; valeur_seuil = "999999" }
$RegleCreee = Invoke-Api POST /api/parametrage/regles $Regle -Jeton $Responsable -Attendu 201
$Regle.valeur_seuil = "888888"
Invoke-Api PUT "/api/parametrage/regles/$($RegleCreee.id_regle)" $Regle -Jeton $Responsable | Out-Null
```

Attendu : `200`, `201`, `200`. Les règles de démonstration : une sortie de
100 unités ou plus est à valider ; un écart d'inventaire de 5 % ou plus
aussi.

### 5.3 Corps d'état

```powershell
$Corps = @{ code_corps_etat = "T$Suffixe"; libelle = "Corps de test"; ordre = 99; couleur = "#123456" }
Invoke-Api POST /api/gammes/corps-etat $Corps -Jeton $Responsable -Attendu 201 | Out-Null
$Corps.couleur = "#654321"
Invoke-Api PUT "/api/gammes/corps-etat/T$Suffixe" $Corps -Jeton $Responsable | Out-Null
Invoke-Api GET /api/gammes/corps-etat -Jeton $Technicien | Format-Table code_corps_etat, libelle, couleur -AutoSize
```

### 5.4 Cycle de vie d'une gamme

Une gamme publiée ne se modifie pas : on en crée une nouvelle version
(brouillon), on la modifie, on la publie ; l'ancienne version est alors
archivée automatiquement.

```powershell
$Gammes = Invoke-Api GET /api/gammes -Jeton $Responsable
$Gammes | Format-Table libelle, version, statut, nombre_etapes -AutoSize
$Duplex = $Gammes | Where-Object { $_.type_logement_code_type -eq "DUPLEX" -and $_.statut -eq "ACTIVE" }
Invoke-Api GET "/api/gammes/$($Duplex.id_gamme)" -Jeton $Responsable | Out-Null
Invoke-Api PUT "/api/gammes/$($Duplex.id_gamme)/etapes" @{ etapes = @() } -Jeton $Responsable -Attendu 409 -Motif GAMME_PUBLIEE
$Brouillon = Invoke-Api POST "/api/gammes/$($Duplex.id_gamme)/versions" -Jeton $Responsable -Attendu 201
Invoke-Api POST "/api/gammes/$($Duplex.id_gamme)/versions" -Jeton $Responsable -Attendu 409 -Motif BROUILLON_EXISTANT
$EtapesModele = @(Invoke-Api GET "/api/gammes/$($Brouillon.id_gamme)/etapes" -Jeton $Responsable)
$Modifiees = @($EtapesModele | ForEach-Object {
    @{ id_etape_modele = $_.id_etape_modele; code = $_.code; libelle = $_.libelle; ordre = $_.ordre
       poids = $_.poids; controle_requis = $_.controle_requis; corps_etat_code_corps_etat = $_.corps_etat_code_corps_etat }
})
$Modifiees[0].libelle = "Fondations (version de test)"
Invoke-Api PUT "/api/gammes/$($Brouillon.id_gamme)/etapes" @{ etapes = $Modifiees } -Jeton $Responsable | Out-Null
Invoke-Api POST "/api/gammes/$($Brouillon.id_gamme)/publication" -Jeton $Technicien -Attendu 403
Invoke-Api POST "/api/gammes/$($Brouillon.id_gamme)/publication" -Jeton $Responsable | Out-Null
Invoke-Api GET /api/gammes -Jeton $Responsable | Where-Object type_logement_code_type -eq "DUPLEX" | Format-Table version, statut -AutoSize
```

Attendu : modifier la gamme active est refusé (`409 GAMME_PUBLIEE`) ;
la nouvelle version est créée (`201`), une seconde est refusée tant que la
première est en brouillon (`409 BROUILLON_EXISTANT`) ; la modification et
la publication passent (`200`), le technicien ne peut pas publier (`403`).
Le tableau final montre la version 1 archivée et la version 2 active.

### 5.5 Archiver une gamme

Seule une gamme active s'archive (un type de logement qui n'est plus
construit). Pour ne pas laisser les duplex sans gamme, on prépare d'abord
une version 3, on archive la version 2, puis on publie la version 3.

```powershell
$Version3 = Invoke-Api POST "/api/gammes/$($Brouillon.id_gamme)/versions" -Jeton $Responsable -Attendu 201
Invoke-Api POST "/api/gammes/$($Version3.id_gamme)/archivage" -Jeton $Responsable -Attendu 409 -Motif GAMME_NON_ACTIVE
Invoke-Api POST "/api/gammes/$($Brouillon.id_gamme)/archivage" -Jeton $Responsable | Out-Null
Invoke-Api POST "/api/gammes/$($Version3.id_gamme)/publication" -Jeton $Responsable | Out-Null
Invoke-Api GET /api/gammes -Jeton $Responsable | Where-Object type_logement_code_type -eq "DUPLEX" | Format-Table version, statut -AutoSize
```

Attendu : la version 3 est créée (`201`) ; archiver un brouillon est
refusé (`409 GAMME_NON_ACTIVE`) ; la version 2 s'archive (`200`) ; la
version 3 est publiée (`200`). Le tableau montre les versions 1 et 2
archivées, la version 3 active.

---

## 6. Stock : mouvements et validations

### 6.1 Lire le stock

```powershell
$IdMagasin = @(Invoke-Api GET /api/magasins -Jeton $Magasinier)[0].id_magasin
$Stock = Invoke-Api GET "/api/magasins/$IdMagasin/stock" -Jeton $Magasinier
($Stock | Where-Object { $_.article.code -eq "A0001" }).stock | Format-List quantite, niveau_alerte
Invoke-Api GET /api/stock/arborescence -Jeton $Gestionnaire | Out-Null
Invoke-Api GET "/api/mouvements?magasin=$IdMagasin&limite=5" -Jeton $Gestionnaire | Format-Table type_mouvement_code_type_mouvement, quantite_saisie, statut_validation -AutoSize
Invoke-Api GET "/api/magasins/$IdMagasin/articles/$Ciment/mouvements" -Jeton $Gestionnaire | Out-Null
Invoke-Api GET "/api/magasins/$IdMagasin/stock" -Jeton $Commercial -Attendu 403
```

Attendu : cinq `200` ; le ciment (`A0001`) affiche sa quantité et son
niveau (`NORMAL`, `MINIMAL`, `CRITIQUE` ou `VIDE`) ; le commercial n'a pas
accès au stock (`403`).

### 6.2 Réception : création, rejeu, conflit

Le téléphone fabrique l'identifiant (`uuid`) de chaque mouvement : s'il
renvoie deux fois le même (réseau coupé), le serveur ne le compte qu'une
fois.

```powershell
$Reception = @{ uuid = [guid]::NewGuid().ToString(); magasin_id_magasin = $IdMagasin; article_id_article = $Ciment
                type_mouvement_code_type_mouvement = "ENT_RECEPTION"; quantite_saisie = "50"; reference_externe = "BL-TEST-$Suffixe" }
(Invoke-Api POST /api/mouvements $Reception -Jeton $Magasinier -Attendu 201).statut_validation
Invoke-Api POST /api/mouvements $Reception -Jeton $Magasinier -Attendu 200 | Out-Null
$Reception.quantite_saisie = "51"
Invoke-Api POST /api/mouvements $Reception -Jeton $Magasinier -Attendu 409 -Motif UUID_DEJA_UTILISE
Invoke-Api POST /api/mouvements $Reception -Jeton $Commercial -Attendu 403
```

Attendu : `201` et statut `VALIDE` (une réception ne se valide pas) ;
`200` au rejeu identique ; `409 UUID_DEJA_UTILISE` si le contenu change ;
`403` pour le commercial.

### 6.3 Contrôles de saisie

```powershell
$Sortie = @{ magasin_id_magasin = $IdMagasin; article_id_article = $Ciment; type_mouvement_code_type_mouvement = "SOR_LOGEMENT"; quantite_saisie = "5" }
Invoke-Api POST /api/mouvements $Sortie -Jeton $Magasinier -Attendu 400 -Motif DONNEES_INVALIDES
$Perte = @{ magasin_id_magasin = $IdMagasin; article_id_article = $Ciment; type_mouvement_code_type_mouvement = "SOR_PERTE"; quantite_saisie = "1" }
Invoke-Api POST /api/mouvements $Perte -Jeton $Magasinier -Attendu 400 -Motif DONNEES_INVALIDES
$Negatif = @{ magasin_id_magasin = $IdMagasin; article_id_article = $Ciment; type_mouvement_code_type_mouvement = "ENT_RECEPTION"; quantite_saisie = "-3" }
Invoke-Api POST /api/mouvements $Negatif -Jeton $Magasinier -Attendu 400 -Motif DONNEES_INVALIDES
```

Attendu : trois `400` : une sortie vers un logement qui ne dit ni quel
logement, ni qui reçoit le matériel, ni pour quel corps d'état, une perte sans motif, une quantité
négative. Le champ `details` de la réponse nomme chaque champ en cause.

### 6.4 Sortie à valider et séparation des tâches

La règle de démonstration rend « à valider » toute sortie de 100 unités ou
plus. Celui qui a saisi ne peut jamais valider sa propre saisie.

```powershell
$Sortie = @{ uuid = [guid]::NewGuid().ToString(); magasin_id_magasin = $IdMagasin; article_id_article = $Ciment
             type_mouvement_code_type_mouvement = "SOR_LOGEMENT"; quantite_saisie = "120"; logement_id_logement = $A01
             beneficiaire = "Équipe gros œuvre A"; corps_etat = "GO" }
(Invoke-Api POST /api/mouvements $Sortie -Jeton $Magasinier -Attendu 201).statut_validation
Invoke-Api GET /api/mouvements/a-valider -Jeton $Gestionnaire | Format-Table uuid, quantite_saisie, statut_validation -AutoSize
Invoke-Api POST "/api/mouvements/$($Sortie.uuid)/validation" @{ decision = "ACCEPTE" } -Jeton $Magasinier -Attendu 403
Invoke-Api POST "/api/mouvements/$($Sortie.uuid)/validation" @{ decision = "ACCEPTE" } -Jeton $Gestionnaire | Out-Null
Invoke-Api POST "/api/mouvements/$($Sortie.uuid)/validation" @{ decision = "REFUSE"; motif = "trop tard" } -Jeton $Admin -Attendu 409 -Motif DECISION_IMPOSSIBLE
```

Attendu : statut `A_VALIDER` ; la sortie apparaît dans la liste à valider ;
le magasinier ne peut pas valider (`403`) ; la gestionnaire valide (`200`) ;
une seconde décision est refusée (`409 DECISION_IMPOSSIBLE`).

```powershell
$SaPropreSortie = @{ uuid = [guid]::NewGuid().ToString(); magasin_id_magasin = $IdMagasin; article_id_article = $Ciment
                     type_mouvement_code_type_mouvement = "SOR_LOGEMENT"; quantite_saisie = "150"; logement_id_logement = $A01
                     beneficiaire = "Équipe gros œuvre A"; corps_etat = "GO" }
Invoke-Api POST /api/mouvements $SaPropreSortie -Jeton $Gestionnaire -Attendu 201 | Out-Null
Invoke-Api POST "/api/mouvements/$($SaPropreSortie.uuid)/validation" @{ decision = "ACCEPTE" } -Jeton $Gestionnaire -Attendu 403 -Motif SEPARATION_DES_TACHES
Invoke-Api POST "/api/mouvements/$($SaPropreSortie.uuid)/validation" @{ decision = "REFUSE" } -Jeton $Admin -Attendu 400 -Motif DONNEES_INVALIDES
Invoke-Api POST "/api/mouvements/$($SaPropreSortie.uuid)/validation" @{ decision = "REFUSE"; motif = "Quantité non justifiée" } -Jeton $Admin | Out-Null
```

Attendu : `403 SEPARATION_DES_TACHES` quand la gestionnaire valide sa
propre sortie ; un refus sans motif est invalide (`400`) ; le refus motivé
par l'administrateur passe (`200`).

À savoir : une sortie refusée **reste déduite du stock** tant qu'elle n'est
pas annulée (le registre des mouvements ne s'efface pas, RG-S8). C'est
l'objet de l'étape suivante.

### 6.5 Annulation par contre-mouvement

Un mouvement ne se modifie ni ne s'efface : on l'annule par un mouvement
inverse, relié à l'original.

```powershell
$Annulation = Invoke-Api POST "/api/mouvements/$($Reception.uuid)/annulation" @{ motif = "Erreur de saisie (test)" } -Jeton $Gestionnaire -Attendu 201
$Annulation | Format-List type_mouvement_code_type_mouvement, quantite_saisie, mouvement_annule_uuid
Invoke-Api POST "/api/mouvements/$($Reception.uuid)/annulation" @{ motif = "encore" } -Jeton $Gestionnaire -Attendu 409 -Motif DEJA_ANNULE
Invoke-Api POST "/api/mouvements/$([guid]::NewGuid())/annulation" @{ motif = "x" } -Jeton $Gestionnaire -Attendu 404
Invoke-Api POST "/api/mouvements/$($SaPropreSortie.uuid)/annulation" @{ motif = "Sortie refusée : remise en stock" } -Jeton $Admin -Attendu 201 | Format-List type_mouvement_code_type_mouvement, quantite_saisie
(Invoke-Api GET "/api/magasins/$IdMagasin/stock" -Jeton $Gestionnaire | Where-Object { $_.article.code -eq "A0001" }).stock | Format-List quantite, niveau_alerte
```

Attendu : `201` et un mouvement `ANN_MOINS` de 50 relié à la réception ;
`409 DEJA_ANNULE` à la seconde tentative ; `404` pour un mouvement
inexistant ; puis l'annulation de la sortie refusée (`ANN_PLUS` de 150) :
la quantité revient en stock. Le ciment est à 8 sacs si le test part de la
démonstration fraîche (128 + 50 − 50 − 120 − 150 + 150).

---

## 7. Stock : seuils, alertes et inventaire

### 7.1 Seuils et alertes

```powershell
Invoke-Api PUT "/api/magasins/$IdMagasin/articles/$Ciment/seuil" @{ seuil_minimal = "80"; seuil_critique = "30" } -Jeton $Gestionnaire -Attendu 204
Invoke-Api PUT "/api/magasins/$IdMagasin/articles/$Ciment/seuil" @{ seuil_minimal = "10"; seuil_critique = "30" } -Jeton $Gestionnaire -Attendu 400
Invoke-Api PUT "/api/magasins/$IdMagasin/articles/$Ciment/seuil" @{ seuil_minimal = "80"; seuil_critique = "30" } -Jeton $Magasinier -Attendu 403
Invoke-Api GET /api/stock/alertes -Jeton $Gestionnaire | Format-Table niveau, message -AutoSize
```

Attendu : `204` ; un seuil critique au-dessus du minimal est refusé
(`400`) ; le magasinier n'a pas ce droit (`403`) ; la liste des alertes
ouvertes.

### 7.2 Inventaire complet

Le magasinier ouvre et compte, la gestionnaire valide les écarts.

```powershell
$Inventaire = Invoke-Api POST /api/inventaires @{ magasin_id_magasin = $IdMagasin } -Jeton $Magasinier -Attendu 201
Invoke-Api POST /api/inventaires @{ magasin_id_magasin = $IdMagasin } -Jeton $Magasinier -Attendu 409 -Motif INVENTAIRE_EN_COURS
Invoke-Api GET "/api/inventaires?magasin=$IdMagasin" -Jeton $Gestionnaire | Out-Null
$Detail = Invoke-Api GET "/api/inventaires/$($Inventaire.id_inventaire)" -Jeton $Magasinier
$Lignes = @($Detail.lignes)
"$($Lignes.Count) lignes à compter"
Invoke-Api POST "/api/inventaires/$($Inventaire.id_inventaire)/soumission" -Jeton $Magasinier -Attendu 409 -Motif COMPTAGE_INCOMPLET
```

Attendu : l'inventaire est ouvert (`201`) avec une ligne par article ; un
second inventaire sur le même magasin est refusé (`409`) ; soumettre avant
d'avoir tout compté aussi (`409 COMPTAGE_INCOMPLET`).

Compter toutes les lignes : chaque article est compté à sa quantité
théorique (zéro si le stock théorique est négatif, une quantité comptée ne
pouvant pas l'être), sauf le ciment, compté avec 10 sacs de plus que la
quantité théorique (écart supérieur à 5 %, donc à valider). Le bloc fait une requête par article
(60) : seul le bilan s'affiche.

```powershell
$Avant = $Bilan.Count
foreach ($ligne in $Lignes) {
    $quantite = [Math]::Max([decimal]$ligne.quantite_theorique, 0)
    if ($ligne.article_id_article -eq $Ciment) { $quantite = $quantite + 10 }
    Invoke-Api PUT "/api/inventaires/$($Inventaire.id_inventaire)/lignes/$($ligne.id_ligne)" @{ quantite_comptee = "$quantite" } -Jeton $Magasinier 6>$null | Out-Null
}
$Ecarts = @($Bilan | Select-Object -Skip $Avant | Where-Object { -not $_.Conforme })
"$($Bilan.Count - $Avant) lignes comptées, $($Ecarts.Count) écart(s)"
Invoke-Api POST "/api/inventaires/$($Inventaire.id_inventaire)/soumission" -Jeton $Magasinier | Out-Null
$LigneCiment = (Invoke-Api GET "/api/inventaires/$($Inventaire.id_inventaire)" -Jeton $Gestionnaire).lignes | Where-Object article_id_article -eq $Ciment
$LigneCiment | Format-List quantite_theorique, quantite_comptee, ecart, statut
```

Attendu : `60 lignes comptées, 0 écart(s)`, soumission acceptée (`200`) ;
la ligne du ciment montre un écart de +10, statut `COMPTEE`.

Chaque ligne est ensuite validée par une autre personne que le compteur.
Accepter un écart inscrit un mouvement d'ajustement ; un écart de 5 % ou
plus exige en plus une seconde validation de cet ajustement, par une
troisième personne (double validation, RG-S9).

```powershell
$UrlInventaire = "/api/inventaires/$($Inventaire.id_inventaire)"
$UrlLigne = "$UrlInventaire/lignes/$($LigneCiment.id_ligne)/validation"
Invoke-Api POST $UrlLigne @{ decision = "ACCEPTE" } -Jeton $Magasinier -Attendu 403
Invoke-Api POST $UrlLigne @{ decision = "ACCEPTE" } -Jeton $Gestionnaire | Out-Null
Invoke-Api POST $UrlLigne @{ decision = "ACCEPTE" } -Jeton $Gestionnaire -Attendu 409 -Motif LIGNE_DEJA_TRAITEE
foreach ($ligne in @((Invoke-Api GET $UrlInventaire -Jeton $Gestionnaire).lignes | Where-Object statut -eq "COMPTEE")) {
    Invoke-Api POST "$UrlInventaire/lignes/$($ligne.id_ligne)/validation" @{ decision = "ACCEPTE" } -Jeton $Gestionnaire 6>$null | Out-Null
}
$Fin = Invoke-Api GET $UrlInventaire -Jeton $Gestionnaire
"Inventaire : $($Fin.statut)"
$Ajustement = ($Fin.lignes | Where-Object article_id_article -eq $Ciment).uuid_ajustement
Invoke-Api POST "/api/mouvements/$Ajustement/validation" @{ decision = "ACCEPTE" } -Jeton $Gestionnaire -Attendu 403 -Motif SEPARATION_DES_TACHES
Invoke-Api POST "/api/mouvements/$Ajustement/validation" @{ decision = "ACCEPTE" } -Jeton $Admin | Out-Null
```

Attendu : le magasinier n'a pas le droit de valider (`403`) ; la
gestionnaire accepte la ligne du ciment (`200`) ; une seconde décision est
refusée (`409 LIGNE_DEJA_TRAITEE`) ; une fois toutes les lignes acceptées,
l'inventaire passe à `VALIDE`. L'ajustement de +10 du ciment (écart
supérieur à 5 %) attend une seconde validation : la gestionnaire, qui l'a
provoqué, ne peut pas la donner (`403 SEPARATION_DES_TACHES`) ;
l'administrateur la donne (`200`).

---

## 8. Avancement des travaux et fiches de route

### 8.1 Lire l'avancement

```powershell
Invoke-Api GET /api/avancement/synthese -Jeton $Commercial | Out-Null
Invoke-Api GET /api/avancement/zones -Jeton $Commercial | Out-Null
Invoke-Api GET /api/avancement/logements -Jeton $Commercial | Format-Table numero, statut, pourcentage_valide, nombre_etapes -AutoSize
$EtapesA01 = @(Invoke-Api GET "/api/logements/$A01/etapes" -Jeton $Chef)
$EtapesA01 | Format-Table ordre, libelle_etape, statut, controle_requis -AutoSize
Invoke-Api GET /api/avancement/etapes-a-valider -Jeton $Chef | Format-Table numero_logement, libelle_etape, nom_auteur_declaration -AutoSize
Invoke-Api GET /api/avancement/synthese -Jeton $Magasinier -Attendu 403
```

Attendu : cinq `200` ; le logement A01 a sa première étape « Fondations »
déclarée terminée par le technicien, en attente de contrôle ; le magasinier
n'a pas accès à l'avancement (`403`).

### 8.2 Valider une étape (et prévenir l'acquéreuse)

```powershell
$Fondations = $EtapesA01 | Where-Object libelle_etape -eq "Fondations"
Invoke-Api POST "/api/etapes/$($Fondations.id_etape)/validation" @{ decision = "ACCEPTE" } -Jeton $Technicien -Attendu 403
Invoke-Api POST "/api/etapes/$($Fondations.id_etape)/validation" @{ decision = "ACCEPTE" } -Jeton $Chef -Attendu 201 | Out-Null
Invoke-Api POST "/api/etapes/$($Fondations.id_etape)/validation" @{ decision = "ACCEPTE" } -Jeton $Chef -Attendu 409
Invoke-Api GET "/api/etapes/$($Fondations.id_etape)/evenements" -Jeton $Chef | Format-Table type_evenement, nom_auteur, horodatage_serveur -AutoSize
```

Attendu : le technicien ne valide pas (`403`) ; le chef valide (`201`) ;
une seconde validation est refusée (`409`) ; l'historique de l'étape montre
la déclaration puis la validation. L'acquéreuse du logement A01 vient de
recevoir une notification (vérifiée au § 12).

### 8.3 Affecter, bloquer, débloquer, déclarer, rejeter

On travaille sur l'étape « Élévation des murs » du logement A01.

```powershell
$Murs = $EtapesA01 | Where-Object libelle_etape -eq "Élévation des murs"
$IdTechnicien = ($Comptes | Where-Object identifiant -eq "technicien").id_utilisateur
Invoke-Api POST /api/fiches-route/affectations @{ etapes = @($Murs.id_etape); technicien_id_utilisateur = $IdTechnicien } -Jeton $Chef | Out-Null
Invoke-Api POST "/api/etapes/$($Murs.id_etape)/blocage" @{ code_motif = "ACCES_IMPOSSIBLE"; commentaire = "Accès bloqué par une livraison" } -Jeton $Technicien -Attendu 201 | Out-Null
Invoke-Api POST "/api/etapes/$($Murs.id_etape)/declaration" @{ commentaire = "Fini" } -Jeton $Technicien -Attendu 409 -Motif TRANSITION_IMPOSSIBLE
Invoke-Api POST "/api/etapes/$($Murs.id_etape)/levee-blocage" @{ commentaire = "Accès rétabli" } -Jeton $Technicien -Attendu 201 | Out-Null
$Declaration = @{ uuid = [guid]::NewGuid().ToString(); commentaire = "Murs montés" }
Invoke-Api POST "/api/etapes/$($Murs.id_etape)/declaration" $Declaration -Jeton $Technicien -Attendu 201 | Out-Null
Invoke-Api POST "/api/etapes/$($Murs.id_etape)/declaration" $Declaration -Jeton $Technicien -Attendu 200 | Out-Null
Invoke-Api POST "/api/etapes/$($Murs.id_etape)/validation" @{ decision = "REFUSE" } -Jeton $Chef -Attendu 400
Invoke-Api POST "/api/etapes/$($Murs.id_etape)/validation" @{ decision = "REFUSE"; motif = "Aplomb à reprendre" } -Jeton $Chef -Attendu 201 | Out-Null
(Invoke-Api GET "/api/logements/$A01/etapes" -Jeton $Chef | Where-Object id_etape -eq $Murs.id_etape).statut
```

Attendu, dans l'ordre : affectation `200` ; blocage `201` ; déclarer une
étape bloquée est refusé (`409 TRANSITION_IMPOSSIBLE`) ; levée `201` ;
déclaration `201`, puis `200` au rejeu du même `uuid` ; un rejet sans motif
est invalide (`400`) ; le rejet motivé passe (`201`) et l'étape revient
`EN_COURS`.

### 8.4 Séparation des tâches sur une étape

Une étape doit être affectée (donc « en cours ») pour être déclarée. Le
chef l'affecte, puis la déclare lui-même pour le compte du technicien : il
ne peut pas la valider ensuite.

```powershell
$Cloisons = $EtapesA01 | Where-Object libelle_etape -eq "Cloisons"
$Gaines = $EtapesA01 | Where-Object libelle_etape -eq "Pose des gaines"
$Elec = $EtapesA01 | Where-Object libelle_etape -eq "Appareillage électrique"
Invoke-Api POST "/api/etapes/$($Elec.id_etape)/declaration" @{ commentaire = "Trop tôt" } -Jeton $Chef -Attendu 409 -Motif TRANSITION_IMPOSSIBLE
Invoke-Api POST /api/fiches-route/affectations @{ etapes = @($Elec.id_etape); technicien_id_utilisateur = $IdTechnicien } -Jeton $Chef | Out-Null
Invoke-Api POST "/api/etapes/$($Elec.id_etape)/declaration" @{ commentaire = "Déclaré par le chef" } -Jeton $Chef -Attendu 201 | Out-Null
Invoke-Api POST "/api/etapes/$($Elec.id_etape)/validation" @{ decision = "ACCEPTE" } -Jeton $Chef -Attendu 403 -Motif SEPARATION_DES_TACHES
Invoke-Api POST "/api/etapes/$($Elec.id_etape)/validation" @{ decision = "ACCEPTE" } -Jeton $Responsable -Attendu 201 | Out-Null
```

Attendu : déclarer une étape « à faire » est refusé
(`409 TRANSITION_IMPOSSIBLE`) ; affectation `200` ; déclaration `201` ;
`403 SEPARATION_DES_TACHES` quand le chef valide sa propre déclaration ;
validation par la responsable technique (`201`).

### 8.5 Fiches de route

```powershell
Invoke-Api GET "/api/fiches-route?statut=OUVERTE" -Jeton $Chef | Format-Table nom_technicien, date_debut, date_fin, statut -AutoSize
$Courantes = @(Invoke-Api GET /api/fiches-route/courante -Jeton $Technicien)
$Fiche = $Courantes[0]
Invoke-Api GET "/api/fiches-route/$($Fiche.id_fiche)" -Jeton $Technicien | Out-Null
Invoke-Api POST /api/fiches-route/affectations @{ etapes = @($Cloisons.id_etape, $Gaines.id_etape); technicien_id_utilisateur = $IdTechnicien; date_prevue = (Get-Date).ToString("yyyy-MM-dd") } -Jeton $Technicien -Attendu 403
$Fiche = Invoke-Api GET "/api/fiches-route/$($Fiche.id_fiche)" -Jeton $Technicien
$Reports = @($Fiche.lignes | Where-Object { $_.etape.statut -notin @("VALIDEE", "TERMINEE_DECLAREE") } | ForEach-Object { @{ id_etape = $_.etape.id_etape; motif = "Reporté à la semaine suivante (test)" } })
Invoke-Api POST "/api/fiches-route/$($Fiche.id_fiche)/cloture" @{ reports = $Reports } -Jeton $Chef | Out-Null
Invoke-Api POST "/api/fiches-route/$($Fiche.id_fiche)/cloture" @{ reports = @() } -Jeton $Chef -Attendu 409 -Motif FICHE_CLOTUREE
```

Attendu : la liste des fiches ouvertes ; la fiche de la semaine du
technicien (`200` deux fois) ; un technicien ne s'affecte pas de travail
(`403`) ; la clôture par le chef, avec un motif pour chaque étape non
terminée (`200`) ; une seconde clôture est refusée (`409 FICHE_CLOTUREE`).

---

## 9. Application mobile : synchronisation et appareils

Un téléphone se connecte avec la même route que le web, en ajoutant la
description de l'appareil : le serveur l'enregistre (enrôlement) et lie le
jeton à cet appareil.

### 9.1 Connexion d'un téléphone

```powershell
$Telephone = @{ empreinte_materiel = "essai-$Suffixe"; plateforme = "android"; version_application = "1.0.0" }
$Mobile = Connect-Compte magasinier -Appareil $Telephone
$Appareils = Invoke-Api GET /api/appareils -Jeton $Admin
$Appareils | Format-Table nom_utilisateur, plateforme, version_application, statut -AutoSize
$IdAppareil = ($Appareils | Where-Object empreinte_materiel -eq "essai-$Suffixe").id_appareil
```

Attendu : `200` deux fois ; l'appareil apparaît, statut `ACTIF`.

### 9.2 Envoyer un lot d'événements

Le téléphone accumule ses saisies hors ligne et les envoie par lots.

```powershell
$Lot = @{
    id_lot = [guid]::NewGuid().ToString(); horodatage_envoi = (Get-Date).ToUniversalTime().ToString("o")
    evenements = @(
        @{ uuid = [guid]::NewGuid().ToString(); type = "MOUVEMENT_STOCK"; horodatage_appareil = (Get-Date).ToUniversalTime().ToString("o")
           charge_utile = @{ magasin_id_magasin = $IdMagasin; article_id_article = $Ciment; type_mouvement_code_type_mouvement = "ENT_RECEPTION"; quantite_saisie = "10" } },
        @{ uuid = [guid]::NewGuid().ToString(); type = "MOUVEMENT_STOCK"
           charge_utile = @{ magasin_id_magasin = $IdMagasin; article_id_article = $Ciment; type_mouvement_code_type_mouvement = "SOR_PERTE"; quantite_saisie = "1" } }
    )
}
$Resultat = Invoke-Api POST /api/synchronisation/lots $Lot -Jeton $Mobile -Attendu 201
$Resultat.resultats | Format-Table statut, code_rejet, motif_rejet -AutoSize
Invoke-Api POST /api/synchronisation/lots $Lot -Jeton $Mobile -Attendu 200 | Out-Null
Invoke-Api POST /api/synchronisation/lots $Lot -Jeton $Magasinier -Attendu 403
```

Attendu : `201` ; un événement `ACCEPTE` (la réception) et un `REJETE`
(la perte sans motif) : un rejet n'empêche pas le reste du lot. Le même
lot renvoyé rend `200` et les mêmes résultats, sans rien retraiter. Un
jeton web, sans appareil, ne peut pas envoyer de lot (`403`).

### 9.3 Données de référence du téléphone

```powershell
$Ref = Invoke-Api GET /api/synchronisation/references -Jeton $Mobile
$Ref.jeux | Format-Table type_donnee, version -AutoSize
$Versions = ($Ref.jeux | ForEach-Object { "$($_.type_donnee)=$($_.version)" }) -join "&"
$Relance = Invoke-Api GET "/api/synchronisation/references?$Versions" -Jeton $Mobile
"Inchangés : $($Relance.inchanges -join ', ')"
"Renvoyés  : $(@($Relance.jeux | ForEach-Object { $_.type_donnee }) -join ', ')"
```

Attendu : la première demande rend tous les jeux autorisés au magasinier
(unités, articles, types de mouvement, motifs de blocage, stock,
notifications) avec leur version ; la seconde, qui annonce ces mêmes
versions, les range tous dans « Inchangés » et la ligne « Renvoyés » reste
vide. Un jeu renvoyé alors que rien n'a changé entre les deux demandes est
une anomalie à signaler (le téléphone retéléchargerait ce jeu à chaque
synchronisation).

### 9.4 Anomalies de synchronisation

Une saisie mobile qui rend le stock négatif crée une anomalie à traiter.

```powershell
$Gros = @{
    id_lot = [guid]::NewGuid().ToString()
    evenements = @(@{ uuid = [guid]::NewGuid().ToString(); type = "MOUVEMENT_STOCK"
        charge_utile = @{ magasin_id_magasin = $IdMagasin; article_id_article = $Ciment; type_mouvement_code_type_mouvement = "SOR_PERTE"; quantite_saisie = "99"; motif = "Sacs détrempés (test)" } })
}
Invoke-Api POST /api/synchronisation/lots $Gros -Jeton $Mobile -Attendu 201 | Out-Null
$Gros.id_lot = [guid]::NewGuid().ToString(); $Gros.evenements[0].uuid = [guid]::NewGuid().ToString()
Invoke-Api POST /api/synchronisation/lots $Gros -Jeton $Mobile -Attendu 201 | Out-Null
$Anomalies = @(Invoke-Api GET "/api/synchronisation/anomalies?statut=OUVERTE" -Jeton $Gestionnaire)
$Anomalies | Format-Table type_anomalie, description -AutoSize
Invoke-Api POST "/api/synchronisation/anomalies/$($Anomalies[0].id_anomalie)/traitement" -Jeton $Gestionnaire | Out-Null
Invoke-Api GET /api/synchronisation/anomalies -Jeton $Technicien -Attendu 403
```

Attendu : deux lots acceptés ; au moins une anomalie `ECART_QUANTITE`
(stock devenu négatif) ; son traitement passe (`200`) ; le technicien n'y
a pas accès (`403`).

### 9.5 Révoquer un téléphone perdu

```powershell
Invoke-Api POST "/api/appareils/$IdAppareil/revocation" -Jeton $Admin | Out-Null
Invoke-Api GET /api/auth/moi -Jeton $Mobile -Attendu 401 -Motif APPAREIL_REVOQUE
Invoke-Api POST "/api/appareils/$IdAppareil/revocation" -Jeton $Gestionnaire -Attendu 403
```

Attendu : la révocation passe (`200`) ; le jeton du téléphone est aussitôt
refusé (`401 APPAREIL_REVOQUE` : l'application efface alors ses données
locales) ; seul l'administrateur révoque (`403`).

---

## 10. Notifications

Chacun ne voit que ses propres notifications.

```powershell
"Non lues : $((Invoke-Api GET /api/notifications/compteur -Jeton $Gestionnaire).non_lues)"
$Notes = @(Invoke-Api GET "/api/notifications?non_lues=true&limite=20" -Jeton $Gestionnaire)
$Notes | Format-Table code_type, message -AutoSize
Invoke-Api POST "/api/notifications/$($Notes[0].id_notification)/lecture" -Jeton $Gestionnaire | Out-Null
Invoke-Api POST "/api/notifications/$($Notes[0].id_notification)/lecture" -Jeton $Magasinier -Attendu 404
"Marquées lues : $((Invoke-Api POST /api/notifications/lecture -Jeton $Gestionnaire).nombre)"
"Non lues : $((Invoke-Api GET /api/notifications/compteur -Jeton $Gestionnaire).non_lues)"
```

Attendu : un compteur non nul ; des notifications de sorties à valider,
de seuils et d'anomalie ; la lecture de l'une (`200`) ; un autre compte
ne peut pas la marquer (`404`, comme si elle n'existait pas) ; la lecture
groupée rend le nombre marqué ; le compteur retombe à `0`.

---

## 11. Pilotage

```powershell
Invoke-Api GET /api/pilotage/stock/synthese -Jeton $Direction | Format-List
Invoke-Api GET "/api/pilotage/stock/mouvements-recents?limite=5" -Jeton $Direction | Out-Null
Invoke-Api GET /api/pilotage/avancement/chantier -Jeton $Direction | Out-Null
Invoke-Api GET /api/pilotage/avancement/zones -Jeton $Direction | Out-Null
Invoke-Api GET /api/pilotage/avancement/logements -Jeton $Direction | Out-Null
Invoke-Api GET /api/pilotage/avancement/corps-etat -Jeton $Direction | Out-Null
Invoke-Api GET /api/pilotage/alertes-etapes -Jeton $Direction | Out-Null
Invoke-Api GET "/api/pilotage/journal?statut=VALIDEE&limite=20" -Jeton $Direction | Out-Null
Invoke-Api GET /api/pilotage/journal/intervenants -Jeton $Direction | Out-Null
$Rapport = Invoke-Api GET /api/pilotage/rapport-hebdomadaire -Jeton $Direction
"Semaine $($Rapport.semaine), du $($Rapport.du) au $($Rapport.au)"; $Rapport.lignes | Format-Table -AutoSize
$Csv = Invoke-Api GET "/api/pilotage/rapport-hebdomadaire?export=csv" -Jeton $Direction
$Csv.Split("`n") | Select-Object -First 4
Invoke-Api GET "/api/pilotage/usage?jours=7" -Jeton $Admin | Format-Table -AutoSize
Invoke-Api GET /api/pilotage/rapport-hebdomadaire -Jeton $Magasinier -Attendu 403
Invoke-Api GET "/api/pilotage/usage?jours=500" -Jeton $Admin -Attendu 400
```

Attendu : douze `200` ; le rapport de la dernière semaine complète, puis
les premières lignes du même rapport en CSV (séparateur `;`) ; le
magasinier n'a pas accès au rapport (`403`) ; une période d'usage hors de
1 à 90 jours est refusée (`400`).

Pour enregistrer le CSV dans un fichier à ouvrir avec un tableur :

```powershell
[System.IO.File]::WriteAllText("$HOME\Desktop\rapport-hebdomadaire.csv", $Csv, (New-Object System.Text.UTF8Encoding($true)))
```

---

## 12. Espace acquéreur

L'acquéreuse voit son logement sans jamais transmettre d'identifiant : le
serveur le déduit de son compte.

```powershell
$MonLogement = Invoke-Api GET /api/acquereur/logement -Jeton $Acquereuse
$MonLogement | Format-List numero_logement, libelle_zone, pourcentage_valide, date_livraison_prevue
$MonLogement.etapes | Format-Table libelle_etape, statut, date_franchissement -AutoSize
Invoke-Api GET /api/acquereur/notifications -Jeton $Acquereuse | Format-Table libelle_etape, date_franchissement, lue -AutoSize
Invoke-Api GET /api/acquereur/logement -Jeton $Chef -Attendu 403
Invoke-Api GET /api/mouvements -Jeton $Acquereuse -Attendu 403
```

Attendu : le logement A01, « Fondations » et « Appareillage électrique »
validées avec leur date (§ 8.2 et 8.4) ; aucun nom d'ouvrier, aucun
commentaire ni motif ; une notification par étape franchie ; le chef
n'accède pas à cet espace et l'acquéreuse n'accède à rien d'autre (`403`).

---

## 13. Exploitation, déconnexion et limitation des tentatives

### 13.1 Métriques et documentation

```powershell
Invoke-Api GET /api/metriques -Jeton $Admin | Out-Null
Invoke-Api GET /api/metriques -Jeton $Direction -Attendu 403
Invoke-Api GET /api/schema/ -Jeton $Admin | Out-Null
Invoke-Api GET /api/docs/swagger/ -Jeton $Admin | Out-Null
Invoke-Api GET /api/docs/redoc/ -Jeton $Admin | Out-Null
Invoke-Api GET /api/schema/ -Jeton $Magasinier -Attendu 403
```

Attendu : métriques et documentation réservées à l'administrateur.

**Tester à la souris** : la page Swagger (`http://127.0.0.1:8000/api/docs/swagger/`)
liste toutes les routes et permet de les essayer. Elle est protégée :
ouverte directement dans un navigateur, sans jeton, elle répond `401`.
Pour l'utiliser, il faut une extension de navigateur qui ajoute l'en-tête
`Authorization: Bearer <jeton>` (le jeton s'obtient avec
`$Admin` dans la console). Le présent guide n'en dépend pas.

### 13.2 Déconnexion

```powershell
$Jetable = Connect-Compte s.traore
Invoke-Api POST /api/auth/deconnexion -Jeton $Jetable -Attendu 204
Invoke-Api GET "/api/audit?action=DECONNEXION&limite=1" -Jeton $Admin | Format-Table horodatage, identifiant_utilisateur, action -AutoSize
Invoke-Api GET /api/auth/moi -Jeton $Jetable | Out-Null
```

Attendu : `204`, puis la déconnexion inscrite au journal d'audit.

**Limite connue** (arbitrage Q2) : le serveur trace la déconnexion mais
n'invalide pas le jeton web, qui reste valable jusqu'à la fin de ses 8 h ;
c'est l'application qui l'oublie. La dernière commande le montre (`200`).
Un jeton mobile, lui, est coupé net par la révocation de l'appareil
(§ 9.5).

### 13.3 Limitation des tentatives de connexion (à faire en dernier)

Au-delà de 10 tentatives par minute sur un même identifiant, ou de 20 par
minute depuis une même adresse, le serveur répond `429` et indique dans
combien de secondes réessayer. **Ce test bloque les connexions depuis le
poste pendant une minute** : le lancer en dernier.

Le bloc enchaîne les tentatives avec un mauvais mot de passe jusqu'au
verrou (sans les compter dans le bilan), puis vérifie qu'une tentative de
plus est bien refusée.

```powershell
$Faux = @{ identifiant = "chef"; mot_de_passe = "faux" }
$Tentatives = 0
do {
    $Tentatives++
    Invoke-Api POST /api/auth/connexion $Faux -Attendu 401 -HorsBilan 6>$null | Out-Null
} while ($DernierCode -eq 401 -and $Tentatives -lt 25)
"Verrou posé après $Tentatives tentatives"
Invoke-Api POST /api/auth/connexion $Faux -Attendu 429 -Motif VERROUILLE
"Réessayer dans $($DerniereErreur.secondes_restantes) s"
```

Attendu : le verrou tombe au plus tard à la onzième tentative (plus tôt si
d'autres connexions ont eu lieu depuis le poste dans la dernière minute,
car l'adresse a aussi son compteur) ; la tentative suivante rend
`[OK] 429 … VERROUILLE` avec le délai d'attente.

---

## 14. Bilan et tableau de couverture

```powershell
Show-Bilan
```

Attendu : **0 écart**. Tout écart est à signaler avec sa ligne, son motif
et son message.

### Ce que couvre ce guide

Chaque opération du contrat (`code/backend/contrat/openapi.yaml`) et
l'étape qui la teste.

| Méthode | Route | Étape |
| --- | --- | --- |
| GET | `/api/sante/vivacite`, `/api/sante/aptitude` | 2.1 |
| POST | `/api/auth/connexion` | 2.2, 2.3, 3.3, 9.1, 13.3 |
| GET | `/api/auth/moi` | 2.4, 2.5, 9.5, 13.2 |
| POST | `/api/auth/deconnexion` | 13.2 |
| GET | `/api/auth/comptes` | 3.1, 3.2 |
| POST | `/api/auth/comptes` | 3.3 |
| PUT | `/api/auth/comptes/{id_utilisateur}` | 3.3, 3.4 |
| GET | `/api/auth/perimetres` | 3.1 |
| GET | `/api/droits/roles`, `/api/droits/permissions` | 3.1 |
| GET, PUT | `/api/droits/accordes` | 3.5 |
| GET | `/api/audit` | 3.6 |
| GET | `/api/appareils` | 9.1 |
| POST | `/api/appareils/{id_appareil}/revocation` | 9.5 |
| GET | `/api/referentiels/chantiers` | 4.1 |
| PUT | `/api/referentiels/chantiers/{id_chantier}` | 4.4 |
| GET | `/api/referentiels/chantiers/{id_chantier}/arborescence` | 4.1 |
| GET | `/api/chantiers/{id_chantier}/logements` | 4.1 |
| POST, PUT | `/api/referentiels/zones`, `/api/referentiels/zones/{id_zone}` | 4.3 |
| POST, PUT | `/api/referentiels/logements`, `/api/referentiels/logements/{id_logement}` | 4.3 |
| GET, POST, PUT | `/api/referentiels/magasins`, `/{id_magasin}` | 4.1, 4.4 |
| GET, POST, PUT | `/api/referentiels/articles`, `/{id_article}` | 4.1, 4.2 |
| GET | `/api/referentiels/categories`, `/unites`, `/types-logement` | 4.1 |
| GET | `/api/types-mouvement`, `/api/motifs-blocage` | 4.1 |
| POST | `/api/import/analyse`, `/api/import/confirmation` | 4.5 |
| GET, POST, PUT | `/api/parametrage/parametres`, `/{id_parametre}` | 5.1 |
| GET, POST, PUT | `/api/parametrage/regles`, `/{id_regle}` | 5.2 |
| GET, POST, PUT | `/api/gammes/corps-etat`, `/{code}` | 5.3 |
| GET | `/api/gammes`, `/api/gammes/{id_gamme}` | 5.4 |
| GET, PUT | `/api/gammes/{id_gamme}/etapes` | 5.4 |
| POST | `/api/gammes/{id_gamme}/versions`, `/publication` | 5.4 |
| POST | `/api/gammes/{id_gamme}/archivage` | 5.5 |
| GET | `/api/magasins`, `/api/magasins/{id_magasin}/stock` | 6.1 |
| GET | `/api/magasins/{id_magasin}/articles/{id_article}/mouvements` | 6.1 |
| GET | `/api/stock/arborescence` | 6.1 |
| GET, POST | `/api/mouvements` | 6.1 à 6.4 |
| GET | `/api/mouvements/a-valider` | 6.4 |
| POST | `/api/mouvements/{uuid_mouvement}/validation` | 6.4 |
| POST | `/api/mouvements/{uuid_mouvement}/annulation` | 6.5 |
| PUT | `/api/magasins/{id_magasin}/articles/{id_article}/seuil` | 7.1 |
| GET | `/api/stock/alertes` | 7.1 |
| GET, POST | `/api/inventaires` | 7.2 |
| GET | `/api/inventaires/{id_inventaire}` | 7.2 |
| PUT | `/api/inventaires/{id_inventaire}/lignes/{id_ligne}` | 7.2 |
| POST | `/api/inventaires/{id_inventaire}/soumission` | 7.2 |
| POST | `/api/inventaires/{id_inventaire}/lignes/{id_ligne}/validation` | 7.2 |
| GET | `/api/avancement/synthese`, `/zones`, `/logements`, `/etapes-a-valider` | 8.1 |
| GET | `/api/logements/{id_logement}/etapes` | 4.3, 8.1, 8.3 |
| POST | `/api/etapes/{id_etape}/validation` | 8.2, 8.3, 8.4 |
| GET | `/api/etapes/{id_etape}/evenements` | 8.2 |
| POST | `/api/etapes/{id_etape}/blocage`, `/levee-blocage`, `/declaration` | 8.3, 8.4 |
| POST | `/api/fiches-route/affectations` | 8.3, 8.5 |
| GET | `/api/fiches-route`, `/courante`, `/{id_fiche}` | 8.5 |
| POST | `/api/fiches-route/{id_fiche}/cloture` | 8.5 |
| POST | `/api/synchronisation/lots` | 9.2, 9.4 |
| GET | `/api/synchronisation/references` | 9.3 |
| GET | `/api/synchronisation/anomalies` | 9.4 |
| POST | `/api/synchronisation/anomalies/{id_anomalie}/traitement` | 9.4 |
| GET | `/api/notifications`, `/api/notifications/compteur` | 10 |
| POST | `/api/notifications/{id_notification}/lecture`, `/api/notifications/lecture` | 10 |
| GET | les 11 routes `/api/pilotage/…` | 11 |
| GET | `/api/acquereur/logement`, `/api/acquereur/notifications` | 12 |
| GET | `/api/metriques`, `/api/schema/`, `/api/docs/…` | 13.1 |

### Ce que ce guide ne couvre pas

- **L'envoi compressé** (`Content-Encoding: gzip`) d'un lot : couvert par
  les tests automatisés.
- **Le renouvellement du jeton mobile** au-delà de 24 h et l'expiration
  (`JETON_EXPIRE`) : il faudrait attendre ; couverts par les tests
  automatisés.
- **Les traitements planifiés** (purges, sauvegarde, relances) : ce ne
  sont pas des routes ; ils se lancent par
  `python manage.py lancer_traitement <nom>` (voir `README.md` du backend).

Les tests automatisés du serveur rejouent tous ces cas et bien d'autres,
sur une base dédiée créée puis détruite à chaque passage :

```powershell
cd code\backend
python -m pytest
```
