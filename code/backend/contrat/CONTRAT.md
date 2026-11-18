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
| Décimaux | `numeric(14,3)` transportés en chaîne (aucune quantité en B1) |
| Collections | tableaux nus, sans enveloppe ni pagination en B1 ; `GET /api/audit` borné par `limite` (1 à 1000, 200 par défaut) |
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
| 403 | `ACCES_REFUSE` ; à la connexion : `COMPTE_INACTIF`, `AUCUNE_AFFECTATION`, `APPAREIL_REVOQUE` |
| 404 | `INTROUVABLE` |
| 405 | `METHODE_NON_AUTORISEE` |
| 409 | `VERROUILLAGE_ADMINISTRATION` |
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

## Écarts avec le contrat simulé des fronts (à reprendre en phase F-06)

- Codes de rôle en `UPPER_SNAKE` (le web les simule en minuscules).
- `droit_accorde.portee` vaut `GLOBALE` ou `PERIMETRE` (arbitrage Q8).
- Ajouts compatibles : `connecte_le`, `id_appareil`, `droits` dans la
  session ; `libelle_chantier` dans l'utilisateur ; bloc `appareil` et
  `mot_de_passe` (création de compte) en entrée ; `GET /api/auth/moi`.
- `id_objet` du journal d'audit toujours `null` (colonne absente du MPD).
- Aucun front n'envoie encore l'en-tête `Authorization` ; le mobile n'envoie
  pas encore le bloc `appareil`.
