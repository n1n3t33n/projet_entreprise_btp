# ChantierSync

**Gestion de chantier hors-ligne pour le BTP ivoirien : le stock et l'avancement des travaux
saisis sur le terrain depuis un smartphone, sans réseau, et consolidés au bureau dès la
reconnexion.**

Projet développé pour **Italia Construction**, filiale ivoirienne du groupe Schiavone, dans le
cadre du module « Atelier du Génie Logiciel » (Institut Ivoirien de Technologie, Licence 3,
année académique 2026-2027).

---

## Table des matières

1. [Contexte et problématique](#1-contexte-et-problématique)
2. [La solution et le périmètre MVP](#2-la-solution-et-le-périmètre-mvp)
3. [Fonctionnalités par module](#3-fonctionnalités-par-module)
4. [Rôles et accès](#4-rôles-et-accès)
5. [Architecture et pile technique](#5-architecture-et-pile-technique)
6. [Modélisation](#6-modélisation)
7. [Structure du dépôt](#7-structure-du-dépôt)
8. [Installation et lancement](#8-installation-et-lancement)
9. [Feuille de route](#9-feuille-de-route)
10. [Liens utiles](#10-liens-utiles)
11. [Équipe et cadre académique](#11-équipe-et-cadre-académique)
12. [Mentions et licence](#12-mentions-et-licence)

---

## 1. Contexte et problématique

Italia Construction est la filiale ivoirienne du groupe Schiavone. Elle conduit des opérations de
construction et de travaux publics en Côte d'Ivoire, avec des chantiers répartis sur plusieurs
sites et un magasin de matériaux par chantier d'importance.

Deux difficultés ont été identifiées lors de l'entretien conduit auprès de l'entreprise le
19 octobre 2026, et consignées dans le cahier des charges.

La première porte sur le **stock de chantier**. Les entrées et les sorties de matériaux sont
tenues sur support papier au magasin, puis ressaisies au bureau avec un décalage de plusieurs
jours. Pendant ce décalage, personne ne connaît l'état réel du stock : les ruptures sont
constatées trop tard, les écarts d'inventaire ne sont rattachables à aucune opération précise, et
la responsabilité d'une sortie de matériel est difficile à établir après coup.

La seconde porte sur l'**avancement des travaux**. L'état d'avancement remonte par échanges
téléphoniques et par comptes rendus de visite. Il n'existe pas de vue consolidée indiquant, à une
date donnée, quelles étapes sont achevées, par qui, et lesquelles sont bloquées. La direction ne
peut donc ni anticiper un retard, ni répondre précisément à un acquéreur qui demande où en est son
logement.

Ces deux difficultés ont une cause commune : **le point où l'information naît — le magasin et le
front de taille — est aussi le point où la couverture réseau est la plus mauvaise**. Toute
solution qui suppose une connexion permanente échoue sur le terrain. C'est la contrainte
structurante du projet.

Le chantier pilote retenu est celui de **Grand-Bassam**.

---

## 2. La solution et le périmètre MVP

ChantierSync est une application mobile destinée aux équipes de terrain, adossée à une API et à un
poste de pilotage web pour le bureau. Le principe directeur est qu'**un agent de terrain doit
pouvoir travailler une journée entière sans réseau** : la saisie est locale, elle est confirmée
immédiatement à l'utilisateur, et la remontée vers le serveur est différée et automatique.

La version 1 couvre trois domaines, délibérément resserrés :

**La gestion du stock d'un magasin de chantier.** Réceptions sur bon de livraison, sorties vers les
équipes, retours et déclarations de casse, seuils d'alerte, inventaires tournants et traitement des
écarts constatés.

**Le suivi de l'avancement par fiches de route.** Les travaux sont décomposés en étapes rattachées
à un corps d'état et à un logement ou une zone. Les techniciens cochent les étapes réalisées sur
une fiche de route, les responsables valident, et l'avancement se consolide automatiquement en un
tableau de bord global et en vues détaillées par corps d'état, avec dates et noms.

**La gestion des droits.** Chaque rôle ne voit et ne fait que ce qui relève de son poste, sur le
périmètre de chantier qui lui est affecté.

Le périmètre du pilote est volontairement étroit, afin que la démonstration porte sur des données
réalistes plutôt que sur un volume artificiel : **un seul magasin**, **50 à 100 références
d'articles**, des **smartphones Android et iOS d'entrée de gamme**, et des **données fictives**
pendant toute la phase de développement. Le passage sur un hébergement réel et sur des données
d'exploitation est subordonné à un accord écrit d'Italia Construction.

Les fonctions destinées à l'**acquéreur du logement**, en consultation seule, sont modélisées mais
placées en **phase 2** : elles ne font pas partie de la version 1.

---

## 3. Fonctionnalités par module

Le produit est découpé en neuf modules fonctionnels. Ce découpage sert de référence commune au
cahier des charges, aux exigences, aux diagrammes et au backlog.

**AUT — Accès et authentification.** Connexion par code PIN utilisable hors réseau, session locale
valable 14 jours avant obligation de reconnexion, enrôlement et révocation des appareils, gestion
des rôles, des permissions et du périmètre d'intervention. Le module porte la règle de séparation
des tâches : l'utilisateur qui émet une opération ne peut pas être celui qui la valide, et ce
contrôle s'applique au niveau de l'événement, pas seulement du rôle.

**REF — Référentiels et paramétrage.** Chantiers et zones, magasins, catalogue d'articles avec
catégories, unités de mesure et conditionnements, corps d'état, gammes de travaux versionnées et
publiées, règles de validation paramétrables par chantier, import de référentiel au format CSV.
Ces données vivent en base et ne sont pas codées en dur, de façon à être modifiables sans
redéploiement.

**STK — Stock.** Saisie d'une réception sur bon de livraison, sortie rapide vers une équipe,
déclaration de retour ou de casse, consultation du stock et détail d'un article hors ligne,
historique des mouvements, seuils et alertes, inventaire tournant et validation des écarts. Les
mouvements de stock sont **immuables** : ils ne sont ni modifiés ni supprimés, et leur statut
n'évolue que par l'ajout d'un événement de validation. L'état du stock est dérivé de ces
événements, jamais écrit directement.

**AVA — Avancement.** Cycle de vie des fiches de route, détail d'une étape et pointage, déclaration
de blocage depuis le terrain, validation des étapes et contrôle qualité, affectation, réaffectation
et délégation d'étape, journal d'audit et traçabilité. Une étape sans contrôle requis est validée
implicitement ; une étape soumise à contrôle attend une validation explicite.

**DSH — Tableaux de bord.** Tableau de bord de la direction, suivi de l'avancement par corps
d'état, tableau de bord du stock et journal d'exécution. Les indicateurs sont des agrégats
recalculés à partir des événements.

**SYN — Synchronisation.** File d'envoi locale, transmission par lots **idempotents** — un lot reçu
deux fois ne produit pas deux écritures —, cache de références pour le travail hors ligne, curseurs
de rafraîchissement par type de donnée, détection et présentation des anomalies et des conflits
dans un centre de synchronisation.

**ADM — Administration.** Comptes utilisateurs et matrice des droits, inventaire des appareils et
révocation, sauvegarde et import, paramétrage fonctionnel de l'application.

**NOT — Notifications.** Abonnements par type d'événement, notifications adressées par destinataire,
alertes de seuil de stock, relance des mouvements restés sans décision au-delà du délai paramétré.

**ACQ — Espace acquéreur (phase 2).** Consultation en lecture seule de l'avancement du logement
concerné. Modélisé, hors version 1.

---

## 4. Rôles et accès

Les accès sont définis par rôle et bornés par un périmètre. Un même utilisateur peut porter
plusieurs rôles, mais toujours sur un périmètre explicitement affecté.

### Rôles de terrain — application mobile

| Rôle | Ce que le rôle fait |
| --- | --- |
| **Magasinier** | Saisit les réceptions, les sorties, les retours et les casses sur son magasin. Consulte le stock. Participe aux inventaires. Ne valide pas ses propres opérations. |
| **Technicien** | Consulte sa fiche de route, coche les étapes réalisées, déclare un blocage. Ne modifie ni le référentiel ni le stock. |
| **Chef de chantier** | Affecte et réaffecte les étapes, valide les déclarations de ses équipes, suit l'avancement de son chantier, valide les sorties de stock qu'il n'a pas saisies. |
| **Gestionnaire de stock** | Pilote le stock au-delà d'un seul magasin : seuils, alertes, inventaires, validation des écarts. |
| **Responsable technique** | Valide les étapes soumises à contrôle qualité, arbitre les blocages, prononce la validation fonctionnelle des livrables. |

### Rôles de bureau — poste de pilotage web

| Rôle | Ce que le rôle fait |
| --- | --- |
| **Direction** | Consulte les tableaux de bord consolidés, l'avancement et les indicateurs de stock. Ne saisit pas d'opération. |
| **Administrateur** | Gère les comptes, les rôles, la matrice des droits, les appareils et les révocations, les référentiels, les sauvegardes et les imports. |
| **Commercial** | Consulte l'avancement des logements pour informer les acquéreurs. |
| **Acquéreur** *(phase 2)* | Consulte, en **lecture seule**, l'avancement du seul logement qui le concerne. |

---

## 5. Architecture et pile technique

L'architecture sépare trois composants qui communiquent uniquement par l'API. Ce découplage est le
choix d'architecture le plus déterminant du projet : il permet de faire évoluer le terrain, le
bureau et le serveur indépendamment.

**Application mobile — Flutter.** Cible Android et iOS depuis une base de code unique, condition
pour tenir le parc hétérogène et d'entrée de gamme des équipes. L'application embarque une base
locale qui porte le stock local, les étapes locales, le journal local, la session locale, le cache
de références et la file d'envoi. C'est cette base locale qui rend la saisie possible sans réseau.

**API — Django REST Framework.** Expose les ressources métier, porte les règles de gestion, la
validation, l'habilitation par rôle et périmètre, et l'intégration des lots de synchronisation.
Les traitements périodiques — relance des mouvements sans décision, ouverture du cycle des fiches
de route, préparation des rapports — sont des commandes de gestion Django déclenchées par
l'ordonnanceur du système.

**Base de données — PostgreSQL.** Les quantités sont stockées en décimal exact et non en virgule
flottante, pour éviter toute dérive sur les cumuls de stock. Les journaux d'événements et le
journal d'audit sont protégés en écriture : un déclencheur rejette toute mise à jour ou suppression,
et les droits correspondants sont retirés au rôle applicatif. Les énumérations sont implémentées
par contrainte de domaine plutôt que par type natif, afin de rester modifiables sans migration de
type.

**Poste de pilotage web — React 18, Vite, TypeScript et Tailwind CSS.** Application à page unique,
découplée du serveur, qui consomme la même API que le mobile. Elle couvre les écrans de bureau :
tableaux de bord, référentiels, administration des comptes et des appareils, paramétrage.

### Mode hors-ligne et synchronisation

Le fonctionnement hors réseau n'est pas un mode dégradé ajouté après coup, c'est le mode normal de
l'application mobile.

À la saisie, l'opération est écrite dans la base locale et confirmée immédiatement à
l'utilisateur ; un événement correspondant est déposé dans la file d'envoi. L'utilisateur n'attend
jamais le réseau.

Au retour du réseau, la file est transmise au serveur **par lots idempotents**. Chaque événement
porte un identifiant stable, ce qui permet au serveur de reconnaître un lot déjà reçu et de ne pas
le rejouer. Le serveur intègre les événements, applique les règles de gestion, puis renvoie les
acquittements et les éventuelles anomalies. Les références consultées hors ligne sont rafraîchies
par curseur, type de donnée par type de donnée, afin de ne pas retélécharger l'intégralité du
catalogue à chaque reconnexion.

Les conflits et les refus ne sont pas masqués : ils sont présentés dans un centre de
synchronisation, avec l'opération concernée et le motif, pour arbitrage humain.

---

## 6. Modélisation

Le dossier [`modélisation/`](modélisation/) contient deux modélisations complémentaires de la même
réalité : une modélisation **UML** orientée objet, et une modélisation **MERISE** orientée système
d'information, dérivée de la première. Chaque diagramme existe en source `.drawio` modifiable et en
export `.svg`.

L'état des lieux détaillé — méthode de dérivation de l'UML vers MERISE, contrôles effectués,
défauts connus et points ouverts — est consigné dans le
[README du dossier de modélisation](modélisation/README.md).

### Cas d'utilisation

![Diagramme de cas d'utilisation — vue d'ensemble](modélisation/uml/cas%20d'utilisation/svg/UC-0%20Cas%20d'utilisation%20-%20Vue%20d'ensemble.drawio.svg)

Vue d'ensemble des acteurs et de leurs cas d'utilisation. Elle situe d'un coup d'œil ce que chaque
rôle peut faire, et sert de table des matières aux quatre diagrammes de détail : gestion du stock,
avancement des travaux, pilotage et référentiels, accès et administration.

### Activité

![Diagramme d'activité — saisie d'un mouvement de stock hors-ligne](modélisation/uml/activité/svg/AC-01%20Activite%20-%20Saisie%20d'un%20mouvement%20de%20stock%20hors-ligne.drawio.svg)

Saisie d'un mouvement de stock sans réseau. Le diagramme montre l'enchaînement complet : contrôle
local, écriture dans la base de l'appareil, confirmation immédiate à l'utilisateur, puis dépôt dans
la file d'envoi. C'est la traduction concrète du principe « la saisie n'attend jamais le réseau ».

### Classes

![Diagramme de classes — accès et droits](modélisation/uml/classes/svg/CL-01%20Classes%20-%20Acces%20et%20droits.drawio.svg)

Domaine de l'identité, des comptes et des droits : utilisateurs, rôles, permissions, affectations
et périmètres. Le modèle complet compte **52 classes** réparties en six domaines, chacun faisant
l'objet d'un diagramme : accès et droits, structure du chantier, catalogue et stock, gamme et
avancement, avancement et notifications, synchronisation et modèle local.

### Séquence

![Diagramme de séquence — synchronisation](modélisation/uml/sequence/svg/SQ-02%20Sequence%20-%20Synchronisation.drawio.svg)

Dialogue entre l'application mobile et le serveur au retour du réseau : constitution du lot, envoi,
intégration, acquittement. Le diagramme fait apparaître le mécanisme d'idempotence, c'est-à-dire ce
qui se passe lorsqu'un lot déjà intégré est renvoyé.

### États-transitions

![Diagramme d'états — mouvement de stock](modélisation/uml/états-transitions/svg/ET-02%20Etats%20-%20Mouvement%20de%20stock.drawio.svg)

Cycle de vie d'un mouvement de stock, de la saisie locale à la décision. Le diagramme justifie un
choix structurant du modèle : le mouvement étant immuable, son statut ne change pas par mise à
jour, mais par ajout d'un événement de validation. Trois autres machines à états complètent
l'ensemble : l'étape de travaux, l'événement en file d'envoi, et l'appareil avec sa session.

### Déploiement

![Diagramme de déploiement — environnement de production du pilote](modélisation/uml/deploiement/svg/DP-02%20Deploiement%20-%20Environnement%20de%20production%20%28pilote%29.drawio.svg)

Répartition des composants sur les machines pour le chantier pilote : appareils de terrain, serveur
applicatif, base de données, poste de pilotage web, et flux entre eux. Un second diagramme décrit
l'environnement de démonstration.

### Modèle conceptuel de données — MERISE

![MCD — carte des domaines](modélisation/merise/svg/MCD/Modèle%20Conceptuel%20de%20Données%20%E2%80%94%20carte%20des%20domaines.drawio.svg)

Carte des six domaines du modèle conceptuel et de leurs points de contact. Le MCD complet compte
**47 entités** et **62 associations**, dont cinq porteuses de propriétés et une ternaire ; il est
disponible en
[vue générale détaillée](modélisation/merise/svg/MCD/MCD%20-%20Modele%20conceptuel%20des%20donnees%20-%20vue%20générale.drawio.svg)
et en six diagrammes par domaine.

### Modèle logique de données — MERISE

![MLD — carte des domaines](modélisation/merise/svg/MLD/Modèle%20Logique%20de%20Données%20%E2%80%94%20carte%20des%20domaines.drawio.svg)

Traduction du MCD en relations : **52 relations** et **68 clés étrangères**. Le modèle physique
PostgreSQL qui en découle compte **52 tables**, **301 colonnes**, **165 contraintes** et
**62 index**.

### Les autres diagrammes

| Famille | Contenu | Emplacement |
| --- | --- | --- |
| Cas d'utilisation | Vue d'ensemble, stock, avancement, pilotage et référentiels, accès et administration | [`uml/cas d'utilisation/`](modélisation/uml/cas%20d'utilisation/) |
| Séquence | Sortie hors-ligne, synchronisation, déclaration et validation d'étape, inventaire et écart, connexion et révocation | [`uml/sequence/`](modélisation/uml/sequence/) |
| Activité | Saisie hors-ligne, synchronisation au retour du réseau, cycle de fiche de route, déclaration et validation d'étape | [`uml/activité/`](modélisation/uml/activité/) |
| Classes | Vue générale et six diagrammes de domaine | [`uml/classes/`](modélisation/uml/classes/) |
| États-transitions | Étape de travaux, mouvement de stock, événement en file d'envoi, appareil et session | [`uml/états-transitions/`](modélisation/uml/états-transitions/) |
| Communication | Sortie de stock et synchronisation | [`uml/communication/`](modélisation/uml/communication/) |
| Paquetage | Découpage en paquets du mobile et du serveur | [`uml/paquetage/`](modélisation/uml/paquetage/) |
| Déploiement | Environnement de démonstration, environnement de production du pilote | [`uml/deploiement/`](modélisation/uml/deploiement/) |
| MERISE | MCD, MCT, MOT, MLD, MPD | [`merise/`](modélisation/merise/) |

---

## 7. Structure du dépôt

```
projet_entreprise_btp/
├── README.md                     ce document
│
├── cadrage/                      documents d'analyse préalable
│   ├── cahier des charges/       cahier des charges v0.1 et présentation
│   │                             synthétique, en .docx et .pdf
│   └── wireframes/               maquettes basse fidélité issues de Figma
│       ├── mobile/               22 écrans terrain + 15 écrans bureau (.png)
│       └── web/                  15 écrans du poste de pilotage (.svg)
│
├── modélisation/                 modélisation UML et MERISE
│   ├── README.md                 méthode, contrôles, défauts connus,
│   │                             points ouverts
│   ├── uml/                      8 familles de diagrammes
│   │   ├── cas d'utilisation/
│   │   ├── sequence/
│   │   ├── activité/
│   │   ├── classes/
│   │   ├── états-transitions/
│   │   ├── communication/
│   │   ├── paquetage/
│   │   └── deploiement/
│   │       chaque famille contient drawio(xml)/ et svg/
│   └── merise/
│       ├── drawio(xml)/          MCD, MCT, MOT, MLD, MPD
│       └── svg/                  mêmes modèles, exportés
│
└── code/                         code applicatif
    ├── backend/                  API Django REST et accès PostgreSQL
    ├── frontend/                 poste de pilotage web React
    └── mobile/                   application Flutter — à créer au sprint mobile
```

Trois précisions sur l'état du dépôt. Les répertoires `code/backend/` et `code/frontend/` sont en
place mais **encore vides** : leur arborescence interne sera posée au début des sprints
correspondants, et `code/mobile/` sera créé de la même façon. Le **backlog priorisé n'est pas
versionné dans le dépôt** : il est tenu sur Notion, pour que l'entreprise puisse suivre
l'avancement en temps réel sans passer par GitHub (voir [Liens utiles](#10-liens-utiles)). Enfin,
les **sources `.drawio` sont conservées à côté de chaque export `.svg`** : les diagrammes restent
modifiables, et le README affiche l'export sans dépendre d'un outil externe.

---

## 8. Installation et lancement

Le code applicatif n'est pas encore écrit. Les procédures ci-dessous décrivent la mise en route
prévue pour chacun des trois composants ; les versions exactes des outils seront arrêtées à
l'ouverture du sprint concerné.

Dans tous les cas, **le développement s'effectue sur des données fictives**. Aucun jeu de données
d'exploitation d'Italia Construction n'est utilisé ni versionné.

### API — Django REST

```bash
cd code/backend

python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env             # renseigner l'accès PostgreSQL

python manage.py migrate
python manage.py loaddata fixtures/demo.json    # jeu de données fictives
python manage.py createsuperuser
python manage.py runserver
```

L'API est alors accessible en local. PostgreSQL doit être démarré et la base créée au préalable.

### Application mobile — Flutter

```bash
cd code/mobile

flutter pub get
flutter devices                  # vérifier l'appareil ou l'émulateur cible
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000
```

L'adresse de l'API est passée à la compilation plutôt que codée en dur, afin de pouvoir viser
indifféremment un serveur local, l'environnement de démonstration ou l'environnement du pilote.
`10.0.2.2` est l'adresse par laquelle l'émulateur Android atteint la machine hôte.

### Poste de pilotage web — React, Vite, TypeScript

```bash
cd code/frontend

npm install
cp .env.example .env             # renseigner VITE_API_BASE_URL
npm run dev
```

Le serveur de développement Vite démarre avec rechargement à chaud. `npm run build` produit les
fichiers statiques de production.

---

## 9. Feuille de route

Le projet suit le découpage en cinq sprints fixé par l'encadrement du module. Les dates précises
restent à arrêter en fonction du calendrier académique et des congés de décembre.

| Sprint | Objet | Livrables |
| --- | --- | --- |
| **1** | Analyse et conception | Visite d'entreprise et entretien, cahier des charges, modélisation UML et MERISE, backlog priorisé, wireframes mobile et web |
| **2** | Développement du front-end web | Poste de pilotage React, écrans de bureau, parcours par rôle |
| **3** | Backend, première partie | API Django REST, modèle de données PostgreSQL, authentification et habilitations |
| **4** | Backend, seconde partie | Synchronisation hors-ligne, règles de gestion, tests, documentation technique |
| **5** | Restitution | Présentations intermédiaires, corrections, présentation finale |

Le sprint 1 est achevé pour ce qui concerne le cahier des charges, la modélisation, le backlog et
les wireframes.

---

## 10. Liens utiles

| Ressource | Accès |
| --- | --- |
| **Maquettes Figma** — écrans mobile et web | [Ouvrir](https://www.figma.com/design/E9NpCmHAATVt8FzWRomWrI/ChantierSync---Mobile---Web) |
| **Suivi de projet** — backlog, sprints, décisions *(équipe et encadrement)* | [Ouvrir](https://wealthy-colony-2ff.notion.site/ChantierSync-Espace-projet-401be86480f281b39c61d6516494412c) |
| **Suivi d'avancement** — vue destinée à Italia Construction | [Ouvrir](https://wealthy-colony-2ff.notion.site/Suivi-ChantierSync-Espace-Italia-401be86480f281f7b186e5c9456bc778) |

---

## 11. Cadre académique

Projet réalisé dans le cadre du module **« Atelier du Génie Logiciel »**, sous l'encadrement de
**M. Sédrick KOUAGNI**, à l'**Institut Ivoirien de Technologie (IIT)** d'Abidjan, en **Licence 3**,
année académique **2026-2027**.

Dépôt et développement : [**n1n3t33n**](https://github.com/n1n3t33n) —
[projet_entreprise_btp](https://github.com/n1n3t33n/projet_entreprise_btp).

Entreprise partenaire : **Italia Construction**, groupe Schiavone, Grand-Bassam.

---

## 12. Mentions et licence

Ce dépôt est un **travail académique**. Il est publié à des fins pédagogiques et d'évaluation.

Les éléments d'identité visuelle du groupe Schiavone utilisés dans les documents de cadrage et les
maquettes demeurent la propriété de leur titulaire et ne sont repris qu'aux fins de la présentation
du projet. Les informations relatives à l'organisation et aux méthodes de travail d'Italia
Construction recueillies lors de l'entretien sont utilisées dans ce seul cadre.

Toutes les données manipulées pendant le développement sont **fictives**. Aucune mise en
exploitation sur des données réelles n'intervient sans accord écrit préalable d'Italia Construction pendant la phase de conception du projet.
