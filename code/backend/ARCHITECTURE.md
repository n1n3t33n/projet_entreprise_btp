# Architecture du backend

Ce document explique comment le code est rangé et pourquoi, pour que tu
puisses ajouter une table, une route ou une règle sans casser l'existant.
L'installation et les commandes sont dans le [README](README.md), les
conventions de l'API dans [`contrat/CONTRAT.md`](contrat/CONTRAT.md).

Deux références décident de tout le reste. Le MPD (`modélisation/`) fixe les
tables, les colonnes et les contraintes. `contrat/openapi.yaml` fixe les
routes et la forme des réponses. On ne déduit jamais l'un de l'autre : une
réponse peut contenir un champ calculé qui n'est pas une colonne, et une
colonne peut ne jamais sortir de l'API.

## Les dossiers

`domaines/` contient le métier, un dossier par domaine du MERISE :
`identite` (MPD-1), `organisation` (MPD-2), `referentiels` (MPD-3), `stock`
(MPD-4), `avancement` (MPD-5 ; les notifications arriveront en B6). Les
domaines synchronisation et acquéreur viendront s'ajouter au même endroit,
sur le même modèle.

`socle/` contient ce qui sert à tous les domaines sans appartenir à aucun :
journaux JSON et identifiant de corrélation, format d'erreur unique,
limitation du taux, santé, partitions mensuelles, import CSV, traitements
planifiés, métriques, alertes par courriel. Le socle n'importe jamais un
domaine. Quand il a besoin d'eux, ce sont les domaines qui viennent s'y
inscrire au démarrage (on y revient plus bas).

`configuration/` assemble le tout : réglages par environnement
(`reglages/base.py`, `developpement.py`, `test.py`, `production.py`) et routes
racines (`urls.py`). C'est le seul endroit qui voit à la fois le socle et les
domaines. Par exemple, la route des métriques est écrite dans le socle, mais
le droit qu'elle exige (`technique.metriques.lire`) est branché dans
`configuration/urls.py`, parce que le socle ne connaît pas la matrice des
droits.

`contrat/` contient le contrat OpenAPI, généré depuis le code et committé,
et `CONTRAT.md` qui l'explique.

`sql/` contient le script de création des trois rôles PostgreSQL et de la
base. Il se lance une fois, en superutilisateur. Tout le reste du schéma
passe par les migrations.

`requirements/` contient les dépendances épinglées : `base.txt` pour tous,
`dev.txt` pour les outils de contrôle, `production.txt` pour le serveur.

## Ce qu'il y a dans un domaine

Prenons `domaines/identite/` :

```
identite/
├── models/        une classe par table du MPD
├── services/      les écritures et les règles métier
├── selecteurs/    les lectures
├── api/           serialiseurs.py, vues.py, routes.py
├── migrations/
├── tests/
├── constantes.py  valeurs des listes fermées (statuts, actions…)
├── demo.py        données de démonstration du domaine
└── apps.py        inscriptions au démarrage
```

Quand un domaine est petit, `services` et `selecteurs` sont de simples
fichiers (`organisation/services.py`) au lieu de dossiers. On les transforme
en dossiers quand ils grossissent ; les imports ne changent pas.

Chaque couche a un rôle précis :

- `models/` décrit les tables : noms de colonnes, contraintes `CHECK`,
  index, tous repris du MPD avec leurs noms (`ck_logement_statut`,
  `ix_zone_chantier_id_chantier`). Un modèle ne contient pas de règle
  métier.
- `services/` contient tout ce qui écrit en base ou applique une règle :
  transactions, verrous, contrôles qui dépendent de l'état de la base,
  journal d'audit. Un service lève une `ErreurApi` quand une règle est
  violée ; il ne sait rien de HTTP.
- `selecteurs/` contient les lectures : filtres, `select_related`,
  agrégats. Il n'écrit jamais.
- `api/` traduit entre HTTP et le domaine. Les sérialiseurs valident
  l'entrée et donnent la forme de la sortie (celle de l'écran qui la
  consomme). Les vues déclarent leur droit, valident, appellent un service
  ou un sélecteur, et rendent la réponse. Une vue ne contient jamais de
  règle métier.

Les listes fermées (statuts, types) sont des contraintes `CHECK` en base,
plus une constante Python dans `constantes.py`. On n'utilise ni type `ENUM`
PostgreSQL ni `choices` figés sur un référentiel vivant : ajouter une valeur
se fait par une migration qui remplace la contrainte.

## Le trajet d'une requête : la révocation d'un appareil

L'administrateur clique sur « Révoquer » dans l'écran Appareils. Le web
envoie :

```
POST /api/appareils/3f2a…/revocation
Authorization: Bearer <jeton>
```

**1. Middlewares.** `socle/journalisation/correlation.py` attribue un
identifiant de corrélation (repris de l'en-tête `X-Request-ID` s'il est
valide), le pose dans le contexte des journaux, chronomètre la requête, puis,
à la sortie, écrit une ligne de journal et alimente les métriques.

**2. Route.** `configuration/urls.py` monte les routes du domaine sous
`/api/`, et `domaines/identite/api/routes.py` les relie aux vues :

```python
path(
    "appareils/<uuid:id_appareil>/revocation",
    vues.VueRevocation.as_view(),
    ...
),
```

**3. Authentification.** DRF appelle `AuthentificationParJeton`
(`identite/authentification.py`). Elle vérifie la signature du jeton, sa
date d'expiration et, à chaque requête, l'état du compte et de l'appareil.
C'est pour ça qu'une révocation bloque immédiatement : à la requête suivante,
le téléphone révoqué reçoit `401 APPAREIL_REVOQUE` et efface ses données
locales.

**4. Droit.** La vue déclare ce qu'elle exige :

```python
class VueRevocation(APIView):
    permission_classes = [IsAuthenticated, ADroit(MODULE_API, "appareils", ACTION_MODIFIER)]
```

`ADroit` (`identite/permissions.py`) cherche dans la matrice des droits
(tables `permission` et `droit_accorde`) si l'un des rôles de l'utilisateur
détient `api.appareils.modifier`. Le droit est une donnée, posée par une
migration de données et réglable depuis l'écran « Matrice des droits » ; il
n'y a aucun `if role == ...` dans le code. Sans le droit : `403
ACCES_REFUSE`.

**5. Vue.** Elle ne fait que passer la main au service, puis mettre en
forme :

```python
def post(self, request: Request, id_appareil: str) -> Response:
    appareil = service_appareils.revoquer(request.user, id_appareil, adresse_client(request))
    return Response(s.AppareilSerializer(appareil).data)
```

**6. Service.** `identite/services/appareils.py` applique la règle EF-AUT-06
dans une transaction, avec un verrou sur la ligne pour que deux révocations
simultanées n'en fassent qu'une :

```python
with transaction.atomic():
    appareil = (
        Appareil.objects.select_for_update()
        .select_related("utilisateur")
        .filter(id_appareil=id_appareil)
        .first()
    )
    if appareil is None:
        raise ErreurApi(statut=404, motif="INTROUVABLE", message="Cet appareil est introuvable.")
    if appareil.statut == STATUT_APPAREIL_REVOQUE:
        return appareil
    appareil.statut = STATUT_APPAREIL_REVOQUE
    appareil.save(update_fields=["statut"])
    audit.consigner(auteur, AUDIT_REVOCATION_APPAREIL, OBJET_APPAREIL, adresse_ip, appareil.pk)
```

Révoquer deux fois ne crée qu'une entrée d'audit. L'entrée d'audit est
écrite dans la même transaction que le changement de statut : soit les deux
existent, soit aucun.

**7. Modèle et base.** `Appareil` (`identite/models/appareil.py`) correspond
à la table `appareil` du MPD-1. Le journal d'audit est une table partitionnée
par mois que le rôle applicatif ne peut ni modifier ni vider : des
déclencheurs refusent `UPDATE`, `DELETE` et `TRUNCATE` (RG-S8).

**8. Réponse.** `AppareilSerializer` (`identite/api/serialiseurs.py`) produit
exactement l'`AppareilDto` attendu par le web, y compris des champs lus à
travers la clé étrangère :

```python
identifiant_utilisateur = serializers.CharField(source="utilisateur.identifiant")
nom_utilisateur = serializers.CharField(source="utilisateur.nom_complet")
```

En cas d'erreur à n'importe quelle étape, `socle/erreurs.py` transforme
l'exception en réponse au format unique (`motif`, `message`, `details`,
`id_correlation`). Les erreurs inattendues donnent `500 ERREUR_INTERNE` avec
l'identifiant de corrélation, qui permet de retrouver la trace complète dans
les journaux sans jamais l'exposer au client.

## La règle de modularité

Un domaine peut LIRE les champs d'un autre domaine à travers une clé
étrangère. Pour toute autre requête sur les tables d'un autre domaine, et
pour toute écriture, il passe par les `services` ou les `selecteurs` de ce
domaine.

Lire à travers une clé étrangère, c'est permis. Une gamme vise un type de
logement, qui appartient au domaine organisation, et la liste des gammes
affiche son libellé (`referentiels/api/serialiseurs.py`) :

```python
libelle_type_logement = serializers.CharField(source="type_logement.libelle", read_only=True)
```

Une requête autonome sur les tables d'un autre domaine passe par ses
sélecteurs. Le jeu de démonstration du domaine identité a besoin du chantier
pilote pour créer les périmètres. Il ne fait pas `Chantier.objects.get(...)`
mais demande au domaine propriétaire (`identite/demo.py`) :

```python
chantier = selecteurs_organisation.chantier_par_code(demo_organisation.CODE_CHANTIER)
```

Une écriture dans un autre domaine passe par ses services. L'import CSV vit
dans le domaine référentiels, mais le journal d'audit appartient au domaine
identité. `referentiels/services.py` appelle donc le service d'audit au lieu
de créer lui-même une ligne `JournalAudit` :

```python
nombre = importation.importer(cible, contenu)
audit.consigner(utilisateur, AUDIT_IMPORT_CSV, OBJET_REFERENTIEL, adresse_ip, cible)
```

L'intérêt de cette règle : le jour où le domaine identité change sa façon
de journaliser (un champ de plus, une autre table), seul son service bouge.

Les dépendances vont dans un seul sens : organisation ne dépend de personne,
référentiels dépend d'organisation, identité lit organisation pour ses
périmètres, stock et avancement dépendent des trois (magasins et logements,
articles, types de mouvement et gammes, auteurs et valideurs). Les couches
`api/` de tous les domaines utilisent `identite.permissions`, qui est
transverse, et `identite.services.portee`, qui traduit la couverture d'un
droit en chantiers et en magasins (le stock filtre par magasin, l'avancement
par chantier).

## Réagir à un autre domaine sans en dépendre à l'envers

Quand un logement est créé, ou qu'une gamme est publiée, l'avancement doit
créer des étapes. L'organisation et les référentiels ne doivent pas
connaître l'avancement : c'est l'avancement qui s'abonne à leurs événements,
dans son `apps.py` :

```python
post_save.connect(
    recepteurs.logement_enregistre, sender=Logement, dispatch_uid="avancement"
)
signaux.gamme_publiee.connect(recepteurs.gamme_publiee, dispatch_uid="avancement")
```

`post_save` est le signal de Django ; `gamme_publiee` est un signal déclaré
par les référentiels (`referentiels/signaux.py`) et émis par leur service de
publication. Les récepteurs (`avancement/recepteurs.py`) appellent un
service du domaine. Un domaine qui veut réagir à un autre fait de même :
l'émetteur déclare un signal, le récepteur s'abonne, la dépendance reste dans
un seul sens.

Le journal d'exécution de l'avancement suit les mêmes règles que ceux du
stock : table immuable et partitionnée, écriture par une seule fonction
(`avancement/services/journal.ecrire`), qui met aussi à jour le statut de
l'étape et recalcule l'avancement agrégé dans la même transaction. Ici le
verrou est un `SELECT … FOR UPDATE` ordinaire : il porte sur `etape_travaux`,
table modifiable, et non sur le journal.

## Les journaux immuables du stock

`mouvement_stock` et `evenement_validation` ne se modifient ni ne se
suppriment (RG-S8), exactement comme le journal d'audit : déclencheurs qui
refusent `UPDATE`, `DELETE` et `TRUNCATE`, et rôle applicatif réduit à
`SELECT` et `INSERT` (`stock/migrations/0002_journaux_immuables.py`). Trois
conséquences dans le code.

Le statut d'un mouvement ne s'écrit qu'une fois, à l'insertion :
`ENREGISTRE`, ou `A_VALIDER` si une règle de validation s'est déclenchée.
Ce que l'écran affiche est calculé à la lecture, à partir des décisions et
d'un éventuel contre-mouvement (`stock/selecteurs.py`) :

```python
if getattr(mouvement, "est_annule", False):
    return STATUT_ANNULE
decision = getattr(mouvement, "derniere_decision", None)
if decision == DECISION_ACCEPTE:
    return STATUT_VALIDE
```

`selecteurs.mouvements()` pose ces deux annotations en une seule requête ;
une vue qui sert des mouvements passe toujours par lui.

On ne corrige jamais un mouvement : on l'annule par un contre-mouvement de
sens opposé, justifié par un motif et relié à l'original
(`services/annulation.py`). Toute écriture au journal passe par une seule
fonction, `services/mouvements.inscrire`, qui recalcule aussi la projection
`stock_courant` dans la même transaction (RG-S2 : le stock est la somme des
mouvements). La saisie, les ajustements d'inventaire, les annulations et
l'import du stock de départ l'appellent tous.

Enfin, `SELECT … FOR UPDATE` est impossible sur ces tables : PostgreSQL exige
le droit `UPDATE` pour poser ce verrou, et le rôle applicatif ne l'a pas.
Deux décisions simultanées sur un même mouvement sont donc sérialisées par
un verrou consultatif (`services/validation.py`) :

```python
curseur.execute(
    "SELECT pg_advisory_xact_lock(hashtext(%s))", [f"mouvement:{uuid_mouvement}"]
)
```

Les tests tournent sous le rôle propriétaire et ne verraient pas ce piège :
`test_la_decision_fonctionne_sous_le_role_applicatif` repasse sous le rôle
applicatif pour le prouver.

## Le socle et les inscriptions au démarrage

Pour que le socle reste indépendant des domaines, chaque domaine s'inscrit
auprès de lui dans `apps.py`, au démarrage. Voici `referentiels/apps.py` :

```python
def ready(self) -> None:
    from domaines.referentiels import demo, importation
    from socle.demo import declarer_chargeur
    from socle.importation import declarer_cible

    # Rang 15 : après l'organisation (types de logement des gammes).
    declarer_chargeur(15, "référentiels", demo.charger)
    # Import CSV (EF-ADM-02).
    declarer_cible(importation.ARTICLES)
```

Les registres existants :

| Registre | Fonction | Utilisé par |
| --- | --- | --- |
| `socle/demo.py` | `declarer_chargeur(rang, domaine, fonction)` | `manage.py charger_demo`, dans l'ordre des rangs |
| `socle/importation.py` | `declarer_cible(CibleImport(...))` | `POST /api/import/analyse` et `/confirmation` |
| `socle/traitements.py` | `declarer_traitement(nom, fonction)` | `manage.py lancer_traitement <nom>` |
| `socle/base_de_donnees/partitions.py` | `declarer_table_partitionnee(nom)` | traitement `creer_partitions` |

Le domaine stock s'y inscrit quatre fois : chargeur de démonstration (rang
30, après l'identité qui fournit les auteurs), cible d'import « stock »,
traitement `relancer_validations` et table partitionnée
`evenement_validation` (`stock/apps.py`). L'avancement s'inscrit de même :
chargeur de rang 40, traitements `cycler_fiches_route` et
`consolider_avancement`, table `evenement_execution`.

## Les rôles PostgreSQL

Django tourne sous `chantiersync_application`, un rôle qui n'est
propriétaire d'aucune table. Il ne peut donc ni modifier la structure, ni
contourner les déclencheurs d'immuabilité. Les migrations passent par la
seconde connexion, `migration`, qui agit sous le rôle propriétaire :

```powershell
python manage.py migrate --database migration
```

Un simple `migrate` échoue, et c'est voulu. Les droits du rôle applicatif
sur les tables futures sont posés une fois pour toutes par
`socle/migrations/0001_fonctions_et_droits.py`. Une nouvelle table n'a donc
besoin d'aucun `GRANT` ; une table immuable, au contraire, se voit retirer
`UPDATE` et `DELETE` par sa propre migration (`identite 0003`, `stock 0002`).

## Où ajouter quoi

**Une table.** Le modèle va dans le `models/` du domaine propriétaire, avec
les noms du MPD (`db_table`, contraintes `ck_`/`uq_`, index `ix_`). Les
valeurs d'une liste fermée vont dans `constantes.py`. Ensuite :

```powershell
python manage.py makemigrations <domaine>
python manage.py migrate --database migration
```

Relis la migration générée. Django ajoute un index `_like` sur les clés
primaires texte, qui n'est pas au MPD : on le retire par une migration
`RunSQL` (voir `referentiels/migrations/0002_retrait_index_hors_mpd.py`).
Ajoute enfin la table à `TABLES_MPD` dans
`identite/tests/test_schema.py`, qui contrôle le schéma réel.

**Une route.**

1. Le sérialiseur dans `api/serialiseurs.py`, à la forme du DTO de l'écran.
2. La vue dans `api/vues.py`, avec son droit :

   ```python
   def get_permissions(self) -> list[Any]:
       return droit("articles", "CREER" if self.request.method == "POST" else "LIRE")
   ```

3. Le chemin dans `api/routes.py`. Si c'est le premier du domaine, inclure
   `routes.py` dans `configuration/urls.py`.

   Si la donnée appartient à un magasin, `ADroit` ne suffit pas : il dit si
   l'utilisateur a le droit, pas sur quel magasin. Le service vérifie en plus
   la portée avec `stock/services/acces.py` (un magasin hors périmètre répond
   404) :

   ```python
   magasin = acces.magasin_autorise(request.user, id_magasin, "stock", "LIRE")
   ```

   Pour une donnée qui appartient à un chantier (une étape, un logement),
   l'avancement fait la même chose avec `avancement/services/acces.py`
   (`etape_autorisee`, `logement_autorise`).
4. La permission, si elle est nouvelle, dans une migration de données qui
   appelle `socle/permissions_donnees.py`. L'administrateur la reçoit
   automatiquement ; les autres rôles se règlent dans la matrice (et dans
   `identite/demo.py` pour la démonstration). Voir
   `referentiels/migrations/0003_permissions.py`.
5. Régénérer le contrat et relire le diff :

   ```powershell
   python manage.py spectacular --file contrat/openapi.yaml --validate
   ```

**Une règle métier.** Elle va dans un service du domaine concerné, jamais
dans une vue ni dans un sérialiseur. Si elle peut être violée, le service lève
une erreur lisible par l'utilisateur, avec les aides de
`socle/api_outils.py` :

```python
raise conflit("GAMME_PUBLIEE", "Une gamme publiée ne se modifie plus : créez-en une nouvelle version.")
```

Le `motif` est destiné au programme, le `message` à l'utilisateur. Le message
ne contient jamais de code interne. Si la règle protège une donnée quoi qu'il
arrive, ajoute aussi une contrainte en base.

**Un traitement planifié.** Une fonction sans argument, idempotente, qui rend
un bilan en une phrase, inscrite avec `declarer_traitement` dans le `ready()`
du domaine. La plateforme la lance avec `manage.py lancer_traitement <nom>` ;
chaque passage est tracé dans `execution_traitement` et un échec envoie une
alerte. Il en existe quatre : `creer_partitions` (quotidien),
`relancer_validations` (horaire, `stock/services/relance.py`),
`cycler_fiches_route` (quotidien, `avancement/services/fiches.py`) et
`consolider_avancement` (nocturne, `avancement/services/agregats.py`).

## Les tests

`pytest` crée sa propre base `test_chantiersync` et la détruit à la fin. Il
ne touche jamais la base de développement. Chaque test tourne dans une
transaction annulée. Les fixtures communes (`client_authentifie(role)`,
`chantier`, `magasin`…) sont dans `conftest.py`. Les tests d'un domaine sont
dans son dossier `tests/` : `test_modeles.py` pour les contraintes en base,
`test_api.py` pour les routes, droits compris.

Deux tests surveillent les deux références. `identite/tests/test_schema.py`
compare le schéma réel au MPD (tables, contraintes, index, nullité).
`socle/tests/test_contrat.py` échoue si le code produit un contrat différent
de `contrat/openapi.yaml`.

Ce document est mis à jour à la fin de chaque jalon.
