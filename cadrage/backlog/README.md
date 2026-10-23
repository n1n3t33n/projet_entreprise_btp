# Backlog priorisé & Roadmap — ChantierSync

Livrables de l'étape « backlog » du module « Atelier du Génie Logiciel » (IIT, Licence 3,
2026-2027), solution **ChantierSync** pour **Italia Construction** (groupe Schiavone).

Ce dossier contient l'export du backlog (`Backlog_ChantierSync_v1.csv`). Le backlog vivant,
ses vues et la feuille de route sont tenus sur Notion. Tout a été produit à partir des
seules sources vérifiées (cahier des charges v0.1, diagrammes UML `.drawio`, MCD) ; rien
n'a été reconstitué de mémoire ou inventé.

## Liens utiles

- **Backlog & suivi (Moi / enseignant)** : https://wealthy-colony-2ff.notion.site/ChantierSync-Espace-projet-401be86480f281b39c61d6516494412c
- **Suivi public (Italia Construction)** : https://wealthy-colony-2ff.notion.site/Suivi-ChantierSync-Espace-Italia-401be86480f281f7b186e5c9456bc778

Sera reporté dans la section « Liens utiles » du README général du projet lors de sa rédaction.
Deux liens pour faciliter la conmpréhension de l'enttreprises qui ne comprendront pas forcément les spécifications techniques du premier lien.

## Contenu : 71 exigences

| Origine | Nombre |
| --- | --- |
| Cahier des charges v0.1 | 65 |
| Nouvelles (modélisation : EF-REF-07 à 10, EF-STK-16) | 5 |
| Créée pour le backlog (EF-AUT-10) | 1 |
| **Total** | **71** |

Répartition par module : AUT 10, REF 10, STK 16, AVA 12, DSH 8, SYN 6, ADM 4, NOT 2, ACQ 3.
Statuts : 57 « À faire », 14 « À arbitrer » (exigences non couvertes par un cas d'utilisation).

## Structure Notion (espace « ChantierSync »)

- **Base « Backlog ChantierSync »** — 71 lignes, 16 propriétés : Titre, Code, Type, Module,
  Priorité MoSCoW, Statut, Origine, Cas d'utilisation, Entité MCD, Règle RG liée, Profils,
  Estimation, Sprint, Dépendances (relation + inverse « Requis par »), Arbitrage/notes, et
  **Phase (proposée)** (formule : MVP / À arbitrer / Phase 2 / Hors MVP, calculée depuis la
  priorité et le statut).
  Vues : *Table*, *Par module*, *Par sprint*, *Kanban (suivi)* (par statut),
  *Roadmap (par priorité)*.
- **Page prof (hub « ChantierSync — Espace projet »)** — présentation du projet, accès à la
  base, puis la **feuille de route** et les vues **Kanban** et **Roadmap** repliées dans la
  continuité du backlog.
- **Page « Suivi ChantierSync — Espace Italia »** (destinée à la publication web) — vue
  épurée *Fonctionnalités par domaine*, la **feuille de route** en langage client, et un
  **Kanban de suivi par état** filtré sur les fonctionnalités métier (sans colonnes
  techniques, sans estimation ni dépendances).

La feuille de route n'est pas une page séparée : elle est intégrée aux deux pages ci-dessus.

## Colonnes du backlog

Code ; Titre (code + libellé exact) ; Type (User story / Tâche technique) ; Module ;
Priorité MoSCoW (M/S/C/W, reprise du cahier ; proposée pour les 6 items nouveaux/créé,
marquée en note) ; Statut (À faire / À arbitrer) ; Origine ; Cas d'utilisation (couverture
UC réelle mesurée dans les `.drawio`, jeu conservé UC-3_pilotage exclu) ; Entité MCD
(rattachement aux 47 entités réelles) ; Règle RG liée (registre des 38 règles) ; Profils ;
Estimation (vide, à chiffrer) ; Sprint (vide, à renseigner selon le découpage de
l'enseignant) ; Dépendances (36 arêtes structurelles) ; Phase (proposée) ; Arbitrage/notes.

## Décisions de cadrage de l'étape

1. **EF-AUT-10 créée** : expiration automatique de la session locale après 14 jours sans
   synchronisation (décision « verrou 14 j », ET-4, corrige H17). Priorité M, entité
   `SessionLocale`.
2. **14 exigences non couvertes** : entrées en statut « À arbitrer », avec recommandation
   d'arbitrage en note (voir ci-dessous).
3. **5 lacunes d'identifiant du MLD (README modélisation § 6.4)** : à remonter en CL-0 en
   v0.2 — `AvancementAgrege` et `StockLocal` reçoivent un identifiant conceptuel propre ;
   `CacheReference`, `StockCourant`, `CurseurReference` sont déjà identifiés relativement.
4. **Suppression de UC-3_pilotage_et_referentiels.drawio + SVG** : confirmée (redondant,
   aucune exigence perdue). Item v0.2.

## Recommandations d'arbitrage des 14 non couvertes

MVP recommandé : EF-AUT-04, EF-AVA-01, EF-SYN-03, EF-SYN-04, EF-SYN-06 (M), EF-SYN-05 (S),
EF-AUT-09 (S, MVP léger ou phase 2).
Phase 2 recommandée : EF-AUT-05, EF-STK-04 (hors pilote mono-magasin), EF-STK-14,
EF-AVA-12, EF-DSH-08, EF-ADM-04, EF-ACQ-03.

## Publication pour Italia

Italia n'a pas de compte Notion : la page de suivi doit être publiée sur le web. Important :
une **vue liée** (linked database) ne s'affiche pas pour un visiteur anonyme tant que la
base source n'est pas elle-même publique. Pour que la page Italia soit lisible publiquement :

1. Publier sur le web la page **« Suivi ChantierSync — Espace Italia »** (Partager → Publier).
2. Publier aussi sur le web la page de la base **« Backlog ChantierSync »**, afin que les
   vues liées de la page Italia se résolvent pour les visiteurs anonymes.

(Alternative si l'on veut garder la base 100 % privée : une base native dédiée, limitée aux
colonnes métier, posée sur la page Italia — à régénérer depuis le CSV.)

## Réimport du CSV

Notion : Importer → CSV → `Backlog_ChantierSync_v1.csv`. Reconvertir ensuite les colonnes
au bon type (Select / Multi-select / Nombre / Relation). L'import crée des blocs : l'espace
ne doit pas être au plafond de blocs gratuits.

## Reste à faire

- Renseigner la colonne **Sprint** et la vue *Par sprint* selon le nombre de sprints fixé
  par l'enseignant.
- Arbitrer les 14 exigences « À arbitrer ».
- Étape suivante : wireframes Figma via Google Stitch.