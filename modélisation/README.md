# Modélisation ChantierSync

Dossier de modélisation de **ChantierSync**, solution de gestion de chantier développée
pour **Italia Construction**, filiale ivoirienne du groupe Schiavone, dans le cadre du
module « Atelier du Génie Logiciel » (IIT, Licence 3, 2026-2027).

Pile technique visée : Flutter (mobile), Django REST (API), PostgreSQL. Le MVP couvre la
gestion du stock, les fiches de route et l'avancement, et la gestion des droits, le tout
utilisable hors-ligne. Le pilote porte sur un seul magasin d'un gros chantier (Bassam ou
Yaou), 50 à 100 références, avec des données fictives.

Le dossier contient deux modélisations complémentaires de la même réalité : une
modélisation **UML** orientée objet, et une modélisation **MERISE** orientée système
d'information. La seconde est dérivée de la première, et cette dérivation est tracée
ci-dessous étape par étape.

---

## 1. Organisation du dossier

```
modélisation/
├── README.md                     ce document
├── uml/
│   ├── cas d'utilisation/        UC-0 à UC-5
│   ├── sequence/                 SQ-1 à SQ-5
│   ├── activité/                 AC-1 à AC-4
│   ├── classes/                  CL-0, CL-1, CL-2, CL-3a, CL-3b, CL-4 à CL-6
│   ├── états-transitions/        ET-1 à ET-4
│   ├── communication/            CO-1
│   ├── paquetage/                PQ-1
│   └── deploiement/              DP-1, DP-2
│       chaque catégorie contient drawio(xml)/ et svg/
└── merise/
    ├── drawio(xml)/              MCD, MCT, MOT, MLD, MPD
    └── svg/
```

---

## 2. Ce qui a été vérifié, et ce qui n'existe pas

Cette section existe parce que plusieurs éléments attendus dans ce README se sont révélés
introuvables. Ils ont été cherchés dans les 2 258 lignes du cahier des charges v0.1
extraites du `.docx`, puis dans les 24 fichiers `.drawio` du dossier `uml/`. Le résultat
est consigné tel quel : rien n'a été reconstitué de mémoire.

### 2.1 Éléments inexistants

| Élément attendu | Résultat de la recherche |
| --- | --- |
| **RG-D11** | Absente. Le cahier des charges s'arrête à RG-D10. Aucun diagramme ne la cite. |
| **H27 à H36** | Absentes. Le registre d'hypothèses de l'annexe A s'arrête à H26, et aucun diagramme ne porte de tag `[H..]`. |
| **EF-AUT-10** | Absente du cahier des charges, qui s'arrête à EF-AUT-09, et absente de tous les diagrammes. UC-4 ne porte que EF-AUT-01, 02, 03, 06, 07 et 08. |
| **Liste des 14 incohérences** | Aucune trace écrite, ni dans le cahier des charges, ni dans les diagrammes. |

Les seules règles RG citées par les diagrammes sont **RG-S1, RG-S4 et RG-A10**, toutes
préexistantes. **Aucune règle RG nouvelle n'a été créée pendant la modélisation**, hormis
RG-D11 ci-dessous.

Un recoupement mérite d'être signalé sans être présenté comme une conclusion :
**exactement 14 exigences du cahier des charges ne sont couvertes par aucun cas
d'utilisation**. Le compte coïncide avec « les 14 incohérences », mais rien ne prouve
qu'il s'agisse de la même liste.

> EF-ACQ-03, EF-ADM-04, EF-AUT-04, EF-AUT-05, EF-AUT-09, EF-AVA-01, EF-AVA-12,
> EF-DSH-08, EF-STK-04, EF-STK-14, EF-SYN-03, EF-SYN-04, EF-SYN-05, EF-SYN-06.

### 2.2 Exigences créées pendant la modélisation

Cinq exigences absentes du cahier des charges v0.1 figurent dans les diagrammes de cas
d'utilisation. Elles sont à intégrer en v0.2. Les libellés ci-dessous sont repris mot pour
mot des fichiers.

| Code | Libellé | Diagramme |
| --- | --- | --- |
| EF-REF-07 | Paramétrer un chantier | UC-3 |
| EF-REF-08 | Définir les règles de validation | UC-3 |
| EF-REF-09 | Publier une version de gamme de travaux | UC-3 |
| EF-REF-10 | Importer un référentiel en CSV | UC-3 |
| EF-STK-16 | Valider un écart d'inventaire | UC-1 |

### 2.3 RG-D11

La séparation des tâches existe déjà au cahier des charges, sous le code **RG-D8** :

> **RG-D8** — Celui qui saisit une opération ne peut pas la valider (séparation des tâches).
> *Justification : contrôle interne et réduction des erreurs.*

La modélisation a durci ce principe en le portant au niveau de l'événement. La règle
correspondante n'existait pas ; elle a été rédigée et validée dans le cadre de ce travail :

> **RG-D11** — Le contrôle de séparation des tâches s'applique à l'événement et non au
> rôle : l'utilisateur qui a émis un événement ne peut pas être celui qui le valide, même
> s'il détient le rôle validateur sur le périmètre concerné.
>
> *Justification : RG-D8 énonce le principe au niveau de l'opération ; la modélisation l'a
> durci au niveau de l'événement pour couvrir les mouvements de stock immuables (RG-S8)
> dont le statut évolue par `EvenementValidation` (RG-S6).*
>
> *Statut : extension de RG-D8, à tracer en v0.2.*

---

## 3. État mesuré de CL-0

Les chiffres ci-dessous ont été mesurés dans le fichier `CL-0_vue_generale.drawio`. En cas
d'écart avec une description antérieure, **le fichier fait foi**.

| Grandeur | Annoncé ailleurs | Mesuré dans le fichier |
| --- | --- | --- |
| Classes | 52 | **52** ✔ |
| Associations | 68 | **67** — le titre inscrit dans le fichier dit lui-même « 67 associations » |
| Encadrés de renvoi dans CL-0 | 8 | **0.** Les renvois sont dans CL-1 à CL-6 : **9** boîtes « X (voir CL-y) » |
| Associations traversantes | 9 | **26** associations inter-domaines |
| Classes dupliquées dans CL-0 | 5 | **0** |

Les 52 classes de CL-0 sont réparties entre CL-1 et CL-6 en une **partition exacte**, sans
aucun recouvrement : 10 + 7 + 6 + 4 + 7 + 8 + 10 = 52. La prémisse de l'hypothèse **H-M1**
(cinq classes dupliquées dans CL-0) ne correspond donc pas au contenu du fichier.

Les neuf renvois présents dans les sous-diagrammes concernent : `Appareil`, `Article`,
`EtapeTravaux`, `EvenementExecution`, `EvenementValidation`, `LigneInventaire`,
`MouvementStock`, `SeuilStock`, `TypeLogement`. `Utilisateur` et `Magasin` n'en ont pas,
alors qu'ils portent respectivement 5 et 3 associations inter-domaines.

---

## 4. Défauts connus et non corrigés dans l'UML

Décision prise : **l'UML reste figé**. Les trois défauts ci-dessous sont donc consignés
ici, et traités au niveau MERISE lorsque cela est nécessaire.

1. **CL-0 n'est pas connexe.** Le graphe se sépare en deux composantes, de 46 et 6 classes.
   La composante détachée est la zone mobile : `CacheReference`, `EtapeLocale`, `FileEnvoi`,
   `JournalLocal`, `SessionLocale`, `StockLocal`. L'association qui la raccorderait,
   `FileEnvoi → LotSynchronisation`, n'existe que dans CL-6 et **est absente de CL-0**.
   → Le MCD la rétablit, sous le verbe *transmis dans*, avec les cardinalités de **H-M2**.

2. **CL-6 : `FileEnvoi → LotSynchronisation` est sans cardinalités.** Elle porte le
   stéréotype « flux HTTPS » et le libellé « envoi de lot idempotent », mais aucune
   cardinalité. → Le MCD les fixe à (0,1) côté `FileEnvoi` et (1,n) côté
   `LotSynchronisation`, conformément à H-M2.

3. **CL-5 : `Notification → EvenementExecution` est sans verbe ni cardinalités.** Cette
   arête **n'existe pas dans CL-0**, qui fait foi pour le périmètre. Elle n'est donc **pas**
   reprise au MCD. Si elle doit exister, il faut d'abord l'ajouter à CL-0 avec un verbe et
   des cardinalités.

### Autres incohérences relevées

- **Deux fichiers UC-3 coexistent.** Ils ne sont pas deux versions du même diagramme :
  `UC-3_referentiels_et_parametrage` couvre EF-REF-01, 02, 04, 05, 06, 07, 08, 09 et 10 ;
  `UC-3_pilotage_et_referentiels` couvre EF-REF-01, 05, 07, 08, 09 plus EF-DSH-01, 02, 03,
  06, EF-STK-13, EF-ACQ-01 et 02. Or **toutes** les exigences DSH et ACQ du second figurent
  déjà dans UC-5. Le second est donc **intégralement redondant** : le supprimer ne perd
  aucune exigence, alors que supprimer le premier perdrait EF-REF-02, 04, 06 et 10.
  → **À supprimer : `UC-3_pilotage_et_referentiels.drawio` et son SVG.**

- **La convention de couleur est rompue dans CL-0.** La légende annonce
  `#dae8fc = Identité, comptes et équipes`, mais 16 classes portent cette couleur, dont
  `Inventaire`, `Logement`, `Gamme`, `FicheRoute` et `EtapeTravaux`. De même, `#ffe6cc`
  fusionne trois domaines et `#fff2cc` « Référentiels paramétrables » héberge
  `AnomalieSynchronisation`. La couleur ne désigne donc plus le domaine. Les diagrammes
  MERISE repartent d'un découpage en six domaines, donné au § 7.

- **Nom de fichier fautif** : `CL-3b_game_et_avancement.drawio` — « game » pour « gamme ».
  Le SVG correspondant est, lui, correctement nommé.

- **Dérive de nommage des SVG** : deux fichiers préfixés `UC-04` ; un `UC-05` intitulé
  « Pilotage et synchronisation » qui ne correspond à aucun diagramme ; `CO-1` exporté en
  `CM-01` et `PQ-1` en `PK-01` ; `UC-0` non aligné sur `UC-01`.

- **H17 est périmé.** Le cahier des charges § 5.4 propose 7 jours d'autonomie avant
  reconnexion, alors que AC-1 et ET-4 retiennent 14 jours, conformément à la décision
  « verrou de session locale à 14 jours ». C'est la v0.2 qui doit être corrigée, pas la
  modélisation.

---

## 5. Méthode de passage de l'UML au MERISE

Le MCD n'est pas une nouvelle analyse : c'est la **traduction de CL-0, classe par classe**.
Deux sources sont utilisées, chacune pour ce qu'elle porte de plus fiable.

- **CL-0 fait foi pour le périmètre** : les 52 classes et les 67 associations, avec leurs
  verbes et leurs cardinalités.
- **CL-1 à CL-6 font foi pour les propriétés** : la vue générale est abrégée à quatre
  attributs par classe, les sous-diagrammes portent le détail. La fusion des deux donne
  **231 propriétés**.

### 5.1 Entité ou association ?

Une classe devient une **association porteuse de propriétés** si et seulement si les trois
conditions suivantes sont réunies :

1. elle a au moins deux pattes, et sa propre multiplicité vaut exactement `1` sur chacune
   d'elles — c'est une jonction vraie ;
2. aucune de ses voisines n'est elle-même transformée en association, MERISE interdisant de
   relier deux associations ;
3. elle n'est ni déclarée immuable par les décisions du projet, ni dotée d'une machine à
   états dans ET-1 à ET-4.

Les identifiants techniques de la forme `idXxx : UUID` **ne comptent pas** comme
identifiants conceptuels : ce sont des artefacts d'implémentation, qui n'apparaissent qu'au
MLD.

Cinq classes satisfont la règle : **`MembreEquipe`** (*appartenir à*), **`DroitAccorde`**
(*accorder*), **`AffectationRole`** (*affecter*, ternaire), **`Conditionnement`**
(*conditionner*) et **`LigneFicheRoute`** (*regrouper*). Les 47 autres restent des entités.

Trois classes auraient pu être prises pour des jonctions et sont restées des entités, pour
des raisons explicites : `EvenementValidation` parce que la décision du projet l'impose
(RG-S8 déclare le mouvement immuable alors que RG-S6 exige que son statut change),
`EvenementExecution` et `FileEnvoi` parce qu'elles sont immuables et portent une machine à
états. `LigneInventaire` et `AbonnementNotification` ont une patte de multiplicité `0..1`
et ne sont donc pas des jonctions.

### 5.2 Conversion des cardinalités

En UML, la multiplicité inscrite à une extrémité compte les objets de **cette** extrémité.
En MERISE, la cardinalité portée par la patte d'une entité compte les occurrences de
**l'association** auxquelles cette entité participe. La cardinalité MERISE d'une entité est
donc la multiplicité UML inscrite **à l'autre bout** de l'association.

| Multiplicité UML à l'autre bout | Cardinalité MERISE |
| --- | --- |
| `1` | **(1,1)** |
| `0..1` | **(0,1)** |
| `1..*` | **(1,n)** |
| `0..*` | **(0,n)** |

Exemple de contrôle : `Chantier —découpé en→ Zone`, multiplicités UML `1` côté Chantier et
`1..*` côté Zone. Un chantier est découpé en 1 à n zones, une zone appartient à un seul
chantier : la patte Chantier porte **(1,n)** et la patte Zone **(1,1)**.

### 5.3 Règles de dérivation du MLD

- **R1** — chaque entité devient une relation ; son identifiant devient la clé primaire.
- **R2** — toute association binaire dont une patte a un maximum de 1 disparaît par
  migration de clé : la clé de l'autre entité devient clé étrangère du côté de maximum 1.
  **57 migrations.**
- **R3** — toute association dont toutes les pattes ont un maximum de n devient une
  relation propre, de clé primaire composée des identifiants participants.
- **R4** — toute association ternaire devient une relation propre. **5 relations issues
  d'associations** au total pour R3 et R4.

Contrôle : 57 migrations + 5 relations = **62**, soit exactement le nombre d'associations
du MCD. Aucune association n'est perdue ni comptée deux fois.

---

## 6. Les cinq modèles MERISE

### 6.1 MCD — `MCD-0_vue_generale.drawio`

**47 entités**, **62 associations** (61 traduites de CL-0, plus la correction du § 4.1),
dont 5 porteuses de propriétés et 1 ternaire. Notation française, cardinalités (0,n),
(1,1), (1,n) et (0,1). Les clés étrangères n'y figurent pas : ce sont des objets du MLD.
Les entités sont des rectangles, les associations des ellipses portant le verbe.

### 6.2 MCT — `MCT_traitements.drawio`

**13 processus** en événement / synchronisation / opération / résultat, soit 21 événements
déclencheurs, 44 actions et 26 résultats, reliés par 13 flux. Chaque processus porte en
gris, sous son libellé, les codes d'exigence et les diagrammes UML dont il est tiré.

Les processus couvrent la saisie hors-ligne, la transmission de la file d'envoi,
l'intégration et le déclenchement des règles, la décision de validation, la relance des
mouvements sans décision, l'inventaire, le cycle de fiche de route, la déclaration et le
contrôle des étapes, l'agrégation de l'avancement, la connexion et le verrou de session, la
révocation, et les notifications.

### 6.3 MOT — `MOT_organisation.drawio`

**22 procédures** réparties sur **8 postes de travail** : magasinier, technicien, chef de
chantier, responsable technique, administrateur fonctionnel, direction et fonctions
support, serveur ChantierSync, acquéreur. Chaque procédure porte sa **nature** — manuel,
automatique ou interactif — et sa **périodicité**, rappelée dans la colonne de gauche.

L'ordonnancement repose sur **cron et des commandes de gestion Django**, conformément à la
décision prise ; Celery n'est envisagé qu'en évolution. Trois traitements sont déclenchés
par l'ordonnanceur : la relance horaire des mouvements sans décision (seuil de 24 h issu de
ET-2), l'ouverture du cycle de fiche de route selon la périodicité paramétrée par chantier,
et la préparation hebdomadaire du rapport.

### 6.4 MLD — `MLD_relations.drawio`

**52 relations** — les 47 entités plus les 5 relations issues d'associations — et **68 clés
étrangères**. Les clés primaires sont soulignées, les clés étrangères préfixées par `#` et
suivies de leur table cible.

Cinq relations n'avaient pas d'identifiant exploitable dans le MCD. Le traitement retenu
est détaillé ci-dessous ; **ce sont des lacunes du modèle conceptuel, pas des choix de
confort**, et elles devraient remonter dans CL-0 en v0.2.

| Relation | Traitement au MLD | Motif |
| --- | --- | --- |
| `CacheReference` | clé naturelle composée `(typeDonnee, cle)` | les deux propriétés existent déjà et identifient la ligne |
| `StockCourant` | identification relative par `seuil_stock_idSeuil` | liaison 1:1 avec `SeuilStock` |
| `CurseurReference` | identification relative `(appareil_idAppareil, typeDonnee)` | un appareil porte un curseur par type de donnée |
| `AvancementAgrege` | **clé technique `idAvancement` ajoutée** | ni identifiant, ni lien vers la portée agrégée dans CL-0 |
| `StockLocal` | **clé technique `idStockLocal` ajoutée** | `CacheReference` alimente (1,n) `StockLocal` : la clé migrée ne distingue pas les lignes |

### 6.5 MPD — `MPD_postgresql.drawio`

**52 tables**, **301 colonnes**, **165 contraintes**, **62 index**, **15 types énumérés**.
Nommage en `snake_case`.

**Types.** `uuid` pour les identifiants techniques ; `varchar(32)` pour les codes
référentiels et les valeurs énumérées ; `varchar(120)` pour les libellés ; `text` pour les
champs libres ; `numeric(14,3)` pour les quantités, afin d'éviter toute dérive de virgule
flottante sur des cumuls de stock ; `integer` et `bigint` pour les compteurs et les numéros
de version ; `date` pour les dates calendaires et `timestamptz` pour les horodatages ;
`jsonb` pour la charge utile des événements et le contenu du cache.

Les clés étrangères reprennent le **type de la clé primaire qu'elles référencent**, et non
systématiquement `uuid` : dix clés primaires sont des `varchar` (`Role`, `Permission`,
`TypeMouvement`, `TypeLogement`, `CategorieArticle`, `UniteMesure`, `CorpsEtat`,
`MotifBlocage`, `TypeNotification`, `CacheReference`).

**Énumérations.** Les 15 types énumérés sont implémentés en `varchar` assorti d'une
contrainte `CHECK`, et non en type `ENUM` natif. Ce choix sert la priorité de modularité :
étendre un `ENUM` PostgreSQL impose une migration de type, alors qu'une contrainte `CHECK`
se remplace. Les référentiels appelés à vivre — rôles, permissions, types de mouvement,
motifs de blocage, règles de validation — ne sont pas des énumérations du tout : ce sont des
tables, conformément à la décision « données en base et non du code ».

**Immuabilité.** Quatre tables sont immuables au sens de RG-S8 : `mouvement_stock`,
`evenement_execution`, `evenement_validation` et `journal_audit`. L'immuabilité est portée
par un déclencheur `BEFORE UPDATE OR DELETE` qui rejette l'opération, doublé d'un retrait
des droits `UPDATE` et `DELETE` au rôle applicatif. Les états sont dérivés des événements,
jamais écrits en dur.

**Partitionnement.** Trois journaux sont partitionnés par `RANGE` mensuel :
`evenement_execution`, `evenement_validation` et `journal_audit`. PostgreSQL impose que la
clé de partitionnement appartienne à la clé primaire ; celle-ci devient donc composite sur
ces trois tables, **ce qui est sans conséquence puisqu'aucune clé étrangère ne les
référence**.

`mouvement_stock` fait exception : elle **est** référencée par `evenement_validation`.
Activer son partitionnement rendrait cette clé étrangère composite `(uuid, date_operation)`
et propagerait la contrainte. Le schéma de partitionnement est donc **défini mais non
activé**, et sera mis en service lorsque le volume le justifiera. Pour un pilote à 50-100
références sur un seul magasin, l'activer immédiatement coûterait de la modularité sans
bénéfice mesurable.

**Index.** Chaque clé étrangère non comprise dans la clé primaire est indexée, PostgreSQL
ne le faisant pas automatiquement. S'y ajoutent des index partiels sur les états chauds —
mouvements restant à valider, stock en alerte, file d'envoi non acquittée —, un index sur
`(statut, date_prevue)` des étapes de travaux, un index antichronologique sur les
notifications par destinataire, et des index `GIN` sur les colonnes `jsonb`.

---

## 7. Conventions de représentation

Les diagrammes MERISE reprennent les conventions maison établies sur le dépôt de référence
`model_site_ecommerce` : titre encadré blanc sur fond blanc, bordure noire, Helvetica 20
gras, en haut ; palette draw.io standard ; aucune note à l'intérieur du schéma ; espacement
large ; fichiers livrés en **XML draw.io non compressé**.

La couleur désigne le **domaine**, jamais le module. Le découpage de CL-0 étant rompu
(§ 4), les six domaines ont été redéfinis à partir de la partition réelle des
sous-diagrammes :

| Couleur | Domaine | Origine |
| --- | --- | --- |
| `#dae8fc` / `#6c8ebf` | Identité, comptes et droits | CL-1 |
| `#d5e8d4` / `#82b366` | Organisation du chantier | CL-2 |
| `#fff2cc` / `#d6b656` | Référentiels et catalogue | CL-3a + CL-3b |
| `#ffe6cc` / `#d79b00` | Stock et journal immuable | CL-4 |
| `#e1d5e7` / `#9673a6` | Avancement et notifications | CL-5 |
| `#f8cecc` / `#b85450` | Synchronisation et modèle local | CL-6 |
| `#f5f5f5` / `#999999` | Acquéreur (phase 2) | — |

Une légende compacte figure en haut à gauche de chaque diagramme, par exception à la règle
« aucune légende à l'intérieur du schéma », comme c'est déjà le cas dans CL-0.

---

## 8. Contrôles effectués avant livraison

Chaque fichier a été passé au même vérificateur automatique : XML bien formé, aucun
chevauchement de boîtes, rien hors canevas, aucune arête pendante, graphe connexe, et —
pour le MCD — aucune association sans verbe ni cardinalités. Le comptage des traits
traversants modélise le routage orthogonal réel de draw.io, et non une simple ligne droite.

| Fichier | Boîtes | Arêtes | Canevas | Traits traversant une boîte |
| --- | --- | --- | --- | --- |
| `MCD-0_vue_generale.drawio` | 110 | 125 | 4825 × 7182 | **3** |
| `MCT_traitements.drawio` | 74 | 73 | 3018 × 3310 | **7** |
| `MOT_organisation.drawio` | 54 | 22 | 3760 × 4610 | **0** |
| `MLD_relations.drawio` | 53 | 68 | 5750 × 3224 | **0** |
| `MPD_postgresql.drawio` | 53 | 68 | 7150 × 4060 | **0** |

Tous les autres contrôles passent sur les cinq fichiers.

Les traits traversants résiduels du MCD et du MCT sont consignés plutôt que masqués. Dans
le MCD, 3 traits sur 125 passent sur une boîte tierce ; dans le MCT, 7 sur 73, et il s'agit
de flux inter-colonnes, tracés en gris pointillé et donc distinguables des liens
structurels. Le MLD et le MPD atteignent zéro parce que leurs relations sont calées sur des
colonnes entières, ce qui aligne les gouttières verticales d'une bande à l'autre et permet
un routage qui ne traverse aucune boîte par construction. La même garantie n'est pas
atteignable sur le MCD sans en revoir la géométrie : **un découpage du MCD par domaine, sur
le modèle de CL-1 à CL-6 et avec les encadrés de renvoi, y parviendrait** et reste
disponible si la lisibilité de la vue générale ne suffit pas.

---

## 9. Points ouverts

### 9.1 Hypothèses de modélisation

| Hypothèse | Statut |
| --- | --- |
| **H-M1** — cinq classes dupliquées dans CL-0 | **Prémisse non vérifiée.** CL-0 porte 52 noms distincts et les sous-diagrammes les partitionnent exactement. Voir § 3. |
| **H-M2** — cardinalités 1..\* / 0..1 sur `FileEnvoi → LotSynchronisation` | **Retenue**, et appliquée au MCD. L'association est absente de CL-0 et sans cardinalités dans CL-6. Voir § 4. |
| **H-M3** — validation implicite d'une étape sans contrôle requis | **Acquise** : ET-1 porte la transition `[à contrôle] validée [sinon] implicite`. |
| **H-M4** — « en alerte » est un statut à part entière | **Acquise** : ET-2 porte l'état « En alerte ». |
| **H-M5** — « déjà reçu » distinct d'« accepté » | **Acquise** : ET-3 porte l'état « Déjà reçu (idempotence) ». |
| **H-M7 à H-M10** — paquetage et déploiement | **Enregistrées sans réexamen** : sans effet sur la modélisation MERISE. |

### 9.2 À traiter en v0.2 du cahier des charges

1. Intégrer **RG-D11** (§ 2.3).
2. Intégrer les cinq exigences **EF-REF-07 à 10** et **EF-STK-16** (§ 2.2).
3. Corriger **H17** : 14 jours et non 7 (§ 4).
4. Statuer sur les **14 exigences non couvertes** par un cas d'utilisation (§ 2.1).
5. Trancher le sort d'**EF-AUT-10**, qui n'existe dans aucune source.
6. Remonter dans CL-0 les **cinq lacunes d'identifiant** relevées au MLD (§ 6.4).
7. Supprimer `UC-3_pilotage_et_referentiels.drawio` et son SVG (§ 4).
8. Renommer `CL-3b_game_et_avancement.drawio` en `CL-3b_gamme_et_avancement.drawio`.
9. Réaligner les noms des SVG sur ceux des `.drawio`.

### 9.3 Dépendance contre-intuitive, conservée

Dans PQ-1, le paquet `aut` dépend de `ref` et non l'inverse, parce que `Perimetre` (module
AUT) délimite `Chantier` et `Magasin` (module REF), alors qu'aucune classe de REF ne
référence AUT. Le graphe reste acyclique, vérifié par tri topologique. La dépendance est
conservée en l'état et signalée ici.
