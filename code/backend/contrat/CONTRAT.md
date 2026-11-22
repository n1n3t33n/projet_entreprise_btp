# Contrat d'API ChantierSync

> **Deux sources de vérité, deux niveaux distincts (arbitrage Q14).**
>
> - Le fichier `openapi.yaml` de ce dossier fait foi pour le **CONTRAT d'API** :
>   chemins, méthodes, formes des requêtes et des réponses, codes d'erreur.
> - Le **MPD** de la modélisation (`modélisation/merise/drawio(xml)/MPD/`) fait
>   foi pour le **SCHÉMA DE DONNÉES** : tables, colonnes, contraintes, index.
>
> On ne déduit **jamais** le schéma de données depuis l'OpenAPI, ni l'inverse.
> Une réponse de l'API peut joindre des champs calculés (`nom_utilisateur`,
> `resume`…) qui ne sont pas des colonnes ; une colonne du MPD peut ne jamais
> être exposée (`mot_de_passe`).

## Comment ce contrat est tenu à jour

1. `openapi.yaml` est **généré depuis le code** (drf-spectacular), jamais
   rédigé à la main, pour qu'il ne dérive pas du comportement réel (exigence
   6.9) :

   ```powershell
   python manage.py spectacular --file contrat/openapi.yaml --validate
   ```

2. Il est **committé**. Toute modification du contrat apparaît donc comme un
   diff relu avec les fronts (web et mobile), comme le veut la démarche
   « contrat d'abord ».
3. Le test `socle/tests/test_contrat.py` échoue si le code produit un contrat
   différent du fichier committé : impossible de changer l'API sans le voir.

## Conventions (rapport B0 § 3, contrat simulé des fronts)

| Sujet | Règle |
| --- | --- |
| Préfixe | `/api`, sans numéro de version (les fronts n'en ont pas) |
| Chemins | en français, sans barre finale (`/api/auth/connexion`) |
| Champs | `snake_case` ; clés étrangères suffixées par leur table (`role_code_role`) |
| Énumérés | `UPPER_SNAKE` (`ACTIF`, `REVOQUE`, `LIRE`…) |
| Identifiants | `uuid` en chaîne, sauf codes des référentiels (`code_role`…) |
| Dates | `AAAA-MM-JJ` ; horodatages ISO 8601 avec fuseau (heure d'Abidjan = UTC) |
| Décimaux | `numeric(14,3)` transportés en chaîne (`"5.000"`) ; en entrée, nombre ou chaîne acceptés |
| Collections | tableaux nus, sans enveloppe ni pagination (référentiels de taille bornée) ; `GET /api/audit` borné par `limite` (1 à 1000, 200 par défaut) |
| Authentification | `Authorization: Bearer <jeton>` ; jeton rendu par `POST /api/auth/connexion` |
| Corrélation | en-tête `X-Request-ID` (uuid) accepté et toujours renvoyé |

## Format d'erreur unique

```json
{ "motif": "UPPER_SNAKE", "message": "phrase en français",
  "details": { "champ": ["raison"] }, "secondes_restantes": 30,
  "id_correlation": "uuid" }
```

`motif` est destiné au programme ; `message` à l'utilisateur et ne contient
jamais de code interne (charte § 8). `details`, `secondes_restantes` et
`id_correlation` n'apparaissent que lorsqu'ils ont un sens.

| Code | Motifs possibles |
| --- | --- |
| 400 | `DONNEES_INVALIDES`, `FORMAT_NON_PRIS_EN_CHARGE` |
| 401 | `NON_AUTHENTIFIE`, `JETON_INVALIDE`, `JETON_EXPIRE` (le mobile redemande le mot de passe) ; `APPAREIL_REVOQUE`, `COMPTE_DESACTIVE` (le mobile **efface ses données locales**, SQ-5 étapes 14-15) ; `APPAREIL_INACTIF` ; à la connexion : `IDENTIFIANTS` |
| 403 | `ACCES_REFUSE` ; `SEPARATION_DES_TACHES` (celui qui a saisi, compté ou déclaré ne valide pas, RG-D8, RG-D11) ; `DECLARATION_INTERDITE` (RG-A3) ; à la connexion : `COMPTE_INACTIF`, `AUCUNE_AFFECTATION`, `APPAREIL_REVOQUE` |
| 404 | `INTROUVABLE` |
| 405 | `METHODE_NON_AUTORISEE` |
| 409 | `VERROUILLAGE_ADMINISTRATION` ; gammes : `BROUILLON_EXISTANT`, `GAMME_PUBLIEE`, `GAMME_NON_BROUILLON`, `GAMME_VIDE`, `GAMME_NON_ACTIVE` ; import : `RIEN_A_IMPORTER` ; stock : `UUID_DEJA_UTILISE`, `STOCK_INSUFFISANT`, `DECISION_IMPOSSIBLE`, `DEJA_ANNULE`, `CONTRE_MOUVEMENT`, `STOCK_INITIAL_EXISTANT` ; inventaire : `INVENTAIRE_EN_COURS`, `COMPTAGE_INCOMPLET`, `ETAPE_INVENTAIRE`, `LIGNE_DEJA_TRAITEE` ; avancement : `TRANSITION_IMPOSSIBLE`, `DECISION_IMPOSSIBLE`, `ETAPE_TERMINEE`, `FICHE_CLOTUREE` |
| 429 | `VERROUILLE` (connexion, EF-AUT-04) ; `TROP_DE_REQUETES` ; en-tête `Retry-After` |
| 500 | `ERREUR_INTERNE` + `id_correlation` |

## En-têtes de session (réponses authentifiées réussies)

- `X-Horodatage-Serveur` : heure du serveur ; le mobile la range dans
  `derniere_connexion_en_ligne` (verrou de 14 jours, AC-1/ET-4). Toute
  requête authentifiée réussie la fournit, synchronisation comprise.
- `X-Jeton-Renouvele` (mobile) : jeton neuf quand le jeton présenté a plus de
  24 h ; le mobile remplace l'ancien.

## Points d'entrée hors schéma

- `GET /api/sante/vivacite` → `200 {"statut":"OK"}`
- `GET /api/sante/aptitude` → `200 {"statut":"OK","verifications":{"base_de_donnees":"OK","migrations":"OK"}}`
  ou `503 {"statut":"INDISPONIBLE", …}`. Publics, sans détail d'infrastructure.
- `GET /api/schema/`, `/api/docs/swagger/`, `/api/docs/redoc/` : documentation
  protégée par le droit « technique / documentation / LIRE ».

`GET /api/metriques` (exigence 6.6) figure dans le schéma ; il est protégé par
le droit « technique / metriques / LIRE » et sert à l'exploitation, pas aux
écrans.

## Import CSV des référentiels (EF-ADM-02)

`POST /api/import/analyse` puis `POST /api/import/confirmation`, avec le même
corps `{"cible": "articles" | "chantiers" | "magasins" | "stock", "contenu":
"<texte du fichier>"}`. La première ligne du fichier est l'en-tête ; les colonnes sont
reconnues par leur nom, dans n'importe quel ordre ; séparateur `;` ou `,`.

| Cible | Colonnes obligatoires | Colonnes facultatives |
| --- | --- | --- |
| `articles` | `code`, `designation`, `unite` | `origine`, `famille`, `code_barre` |
| `magasins` | `code`, `nom`, `chantier` (code) | — |
| `chantiers` | `code`, `nom` | `programme`, `date_debut` (AAAA-MM-JJ ou JJ/MM/AAAA) |
| `stock` | `magasin` (code), `article` (code), `quantite` | `seuil_minimal` et `seuil_critique` (ensemble) |

La cible `stock` inscrit le stock de départ comme un mouvement
`ENT_STOCK_INITIAL` au nom de la personne qui importe ; une ligne est
identifiée par le couple (magasin, article) et un article n'a qu'un stock de
départ par magasin.

L'analyse n'écrit rien et rend `colonnes`, une ligne de rapport par ligne de
données et les totaux. La confirmation refait l'analyse, écrit les lignes
valides (création ou mise à jour par code) et journalise `IMPORT_CSV`. Un
en-tête inconnu ou incomplet rend `400 DONNEES_INVALIDES` avec la liste des
colonnes possibles dans `details.contenu`.

## Stock (B3)

- `POST /api/mouvements` est idempotent sur `uuid`, généré par le client
  (téléphone hors ligne) : premier envoi `201`, rejeu identique `200` avec le
  même mouvement, même `uuid` et contenu différent `409 UUID_DEJA_UTILISE`.
  Sans `uuid`, le serveur en attribue un. Même règle pour une décision
  (`uuid` de l'événement).
- `statut_validation` servi est dérivé : `VALIDE`, `A_VALIDER`,
  `EN_ALERTE` (au-delà du délai de relance), `REJETE`, `ANNULE`. En base, seul
  le statut d'insertion est écrit.
- Un mouvement ne se corrige pas : `POST /api/mouvements/{uuid}/annulation`
  inscrit un contre-mouvement (`ANN_PLUS` ou `ANN_MOINS`) relié à l'original
  par `mouvement_annule_uuid`.
- Un magasin hors du périmètre de l'utilisateur répond `404`, comme un magasin
  inexistant.
- Routes sans écran web à ce jour (forme définie côté serveur, F-12) :
  `GET /api/mouvements/a-valider`, `POST /api/mouvements/{uuid}/validation`,
  `/annulation`, `GET /api/stock/alertes` et toutes les routes
  `/api/inventaires`.

## Avancement (B4)

- Les étapes d'un logement naissent de la gamme active de son type ; il n'y a
  pas de route de création. Statuts : `A_FAIRE`, `EN_COURS`,
  `TERMINEE_DECLAREE`, `BLOQUEE`, `VALIDEE`.
- `POST /api/etapes/{id}/declaration`, `/blocage`, `/levee-blocage` et
  `/validation` sont idempotents sur l'`uuid` de l'événement (téléphone hors
  ligne) : `201` au premier envoi, `200` au rejeu. La déclaration rend un ou
  deux événements : une étape sans contrôle est validée implicitement.
- Décision de contrôle : `{"decision": "ACCEPTE" | "REFUSE", "motif"}`,
  motif obligatoire au rejet.
- `est_delegation` vaut vrai quand l'auteur a déclaré pour le compte du
  technicien affecté (`pour_le_compte_de_id_utilisateur`,
  `nom_pour_le_compte_de`).
- Pourcentages en chaîne à trois décimales ; `id_cible` d'un agrégat de
  corps d'état : « id du chantier:code du corps d'état ».
- Routes sans écran web à ce jour (F-13) : `/api/fiches-route*`,
  `/api/etapes/{id}/declaration`, `/api/etapes/{id}/levee-blocage`.

## Écarts avec le contrat simulé des fronts (à reprendre en phase F-06)

- Codes de rôle en `UPPER_SNAKE` (le web les simule en minuscules).
- `droit_accorde.portee` vaut `GLOBALE` ou `PERIMETRE` (arbitrage Q8).
- Ajouts compatibles : `connecte_le`, `id_appareil`, `droits` dans la
  session ; `libelle_chantier` dans l'utilisateur ; bloc `appareil` et
  `mot_de_passe` (création de compte) en entrée ; `GET /api/auth/moi`.
- `id_objet` du journal d'audit : renseigné depuis B2 (appareil, compte ou
  cible d'import visés) ; colonne hors MPD, écart validé (Q-C, dette v0.2).
- Aucun front n'envoie encore l'en-tête `Authorization` ; le mobile n'envoie
  pas encore le bloc `appareil`.

Écarts introduits en B2 (référentiels) :

- Deux formes pour le magasin, chacune à la forme de son écran (I-30) :
  `GET /api/referentiels/magasins` rend `nom` et `chantier_id_chantier`,
  `GET /api/magasins` (écran Stock) rend `libelle` et `id_chantier`.
- Statut du logement : cycle de vie `A_VENIR`, `EN_COURS`, `LIVRE`
  (arbitrage Q-A) ; l'écran Référentiels du web en simule un autre (I-34).
- Familles d'articles plates (Q-E) : `code_parent` toujours `null`.
- Paramètres de chantier : `chantier_id_chantier` ajouté, facultatif en
  entrée tant qu'il n'existe qu'un chantier (I-35).
- Codes d'étape de gamme suffixés par version (`EM-01~V2`) : le code est
  unique sur tout le catalogue au MPD (I-36).
- Colonnes de l'import tirées du MPD et non de la simulation (I-37).
- Énumération `{ACTIF, INACTIF}` nommée `StatutActiviteEnum` dans le schéma
  (anciennement `StatutEnum`, mêmes valeurs).

Écarts introduits en B3 (stock) :

- Corps de `POST /api/mouvements` : le web envoie déjà `corps_etat`,
  `beneficiaire`, `motif` et `code_unite`, qui n'existaient pas au MPD-4 ;
  ils sont désormais en base (écarts Q-L). Ajouts compatibles en sortie :
  `code_unite`, `corps_etat`, `beneficiaire`, `horodatage_appareil`,
  `mouvement_annule_uuid`, `derive_horloge` (RG-S11).
- `ArticleDto` de l'écran Stock : `code_categorie` peut valoir `null`
  (article sans famille).
- Types de mouvement employés par le serveur : `ENT_STOCK_INITIAL`,
  `AJU_INVENTAIRE_PLUS`, `AJU_INVENTAIRE_MOINS`, `ANN_PLUS`, `ANN_MOINS` ; ils
  ne se saisissent pas. Le mobile n'a qu'`AJU_INVENTAIRE` (I-21).
- Niveau `VIDE` (stock nul ou négatif) ajouté aux niveaux du MPD, comme le
  web l'affiche.

Écarts introduits en B4 (avancement) :

- Décision de contrôle d'une étape en `ACCEPTE` / `REFUSE` ; le web envoie
  encore `valider` / `rejeter` (I-30).
- Troisième forme de la zone (`ZoneDto` du module Avancement : `nom`,
  `id_chantier`), servie par `GET /api/avancement/zones`.
- Corps de `POST /api/etapes/{id}/blocage` : `article_id_article` ajouté
  pour un manque de matériel (RG-A10).
- Le mobile manipule des notions absentes du MPD (pointage, pause, gravité
  et retard estimé d'un blocage, métré, points de contrôle) : non servies
  (Q-AC).
