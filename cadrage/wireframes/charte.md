# Charte graphique & spécifications d'interface — ChantierSync

Document de référence pour la conception des interfaces de **ChantierSync**, ma solution de gestion
de chantier développée pour **Italia Construction** (le groupe Schiavone). Il fixe l'identité visuelle,
les composants et les règles d'interface communes aux **deux plateformes** : l'application mobile de
chantier (terrain) et le poste de pilotage web (bureau).

Toute interface du projet, mobile ou web, applique cette charte afin de garantir une expérience
cohérente, lisible et professionnelle.

---

## 1. Identité visuelle

- **Logo** : bloc-marque « SCHIAVONE GROUP » (emblème de façade de bâtiment + nom de marque). Il est
  utilisé dans un **composant unique**, décliné sur fond marine (barre de navigation) et sur fond
  clair. Aucune variante tronquée ni recomposée.
- **Style** : *flat design* sobre et institutionnel. Pas de dégradés inutiles, pas d'ombres lourdes.
  Priorité à la lisibilité, y compris en extérieur sur un chantier.
- **Ton** : rassurant, factuel, orienté métier du BTP.

## 2. Palette de couleurs

| Rôle | Couleur | Usage |
| --- | --- | --- |
| Primaire (marine) | `#002E5E` | Barres de navigation, boutons principaux, titres forts |
| Secondaire (sarcelle) | `#1F7FA8` | Liens, accents interactifs, éléments secondaires |
| Accent (or) | `#8A6508` | Alertes de seuil, badges, indicateurs à surveiller |
| Or clair | `#FBF1CF` / `#F6DF94` | Surbrillance de sélection, fonds de badge |
| Fonds | `#F3F8FC` / `#EAF6FC` | Arrière-plans de page et de sections |
| Texte principal | `#2B3A4A` | Corps de texte, intitulés |
| Texte secondaire | `#5A6572` | Sous-titres, légendes (jamais un gris trop pâle) |
| Texte atténué | `#9AA5B1` | Mentions discrètes |
| Succès | `#2E7D32` | Validation, conformité |
| Danger | `#C0392B` | Blocage, état critique |

**Contraste** : tout texte respecte un ratio de contraste **≥ 4,5:1**. Un statut n'est **jamais**
porté par la couleur seule (toujours une icône + un libellé).

## 3. Typographie

- **Police unique** : **Plus Jakarta Sans** sur toutes les plateformes.
- **Graisses** : 700 (titres), 600 (sous-titres et libellés forts), 500 (libellés), 400 (corps).
- **Échelle indicative** : Titre 1 ≈ 28–32, Titre 2 ≈ 20–22, Titre 3 ≈ 16–18, corps ≈ 14–16,
  mention ≈ 12–13.

## 4. Iconographie

- **Jeu d'icônes** : **Phosphor**, style *outline* (traits fins), taille homogène.
- Les icônes accompagnent toujours un libellé pour les actions et les statuts.
- **Aucun emoji** ni glyphe décoratif utilisé comme icône.

## 5. Formes, espacement et élévation

- **Rayons d'angle** : cartes **16 px**, boutons et champs **12 px**, pilules **plein arrondi**.
- **Ombres** : légères et uniformes (ex. `0 1px 2px rgba(0,0,0,0.06)`), bordures fines `#E3EDF5`.
- **Espacement** : échelle régulière 4 / 8 / 16 / 24 / 32.
- **Grilles** : web en **12 colonnes** (référence 1280–1440 px, marge latérale 32 px) ; mobile en
  colonne unique (référence 390 px, marge 16 px).
- **Cibles tactiles** (mobile) : boutons principaux ≥ 56 px de haut.

## 6. Composants d'interface

- **Boutons** : primaire (fond marine, texte blanc), secondaire (contour marine). Hauteur web 44 px.
- **Champs de saisie** : coins 12 px, icône de contexte, état d'erreur en ligne (jamais de fenêtre
  d'alerte système).
- **Cartes** : blanches, coins 16 px, ombre douce.
- **Indicateurs clés (KPI)** : icône + grand nombre + libellé + variation éventuelle.
- **Tableaux** : en-tête collant, lignes de 56 px, colonne de sélection multiple + barre d'actions
  groupées, pagination légère. Débordement horizontal géré par défilement.
- **Pilules de statut** : icône + libellé (À faire, En cours, Terminée, En retard, Critique…).
- **Jauge de seuils** : barre à quatre niveaux **Vide / Critique / Mini / Plein**, avec
  représentation explicite du **stock négatif** (anomalie signalée, non bloquante).
- **Tiroirs latéraux** (panneaux de détail/édition), **modales** de confirmation, **onglets**,
  **filtres** en pilules.
- **Bandeau de synchronisation** : état simple (éléments en attente d'envoi, dernière
  synchronisation, état de la connexion).

## 7. Mouvement : animations et transitions

Les animations restent discrètes et porteuses de sens, inspirées d'interfaces réelles et cohérentes.

- **Apparition** des listes, lignes et grilles : révélation **en cascade** (≈ 200 ms par élément,
  léger décalage).
- **Survol** des cartes : légère lévitation (translation de quelques pixels + ombre renforcée),
  ≈ 240 ms ; survol des boutons/lignes : micro-retour (~1 px), ≈ 160 ms.
- **Changement de page/section** : fondu + légère montée, ≈ 240 ms.
- **Tiroirs** : glissement depuis la droite ; **modales** : fondu + léger agrandissement.
- N'animer que la transformation et l'opacité (jamais les dimensions).
- **Accessibilité** : respect de la préférence « réduire les animations » (rendu final immédiat si
  l'utilisateur la demande).

## 8. Règles de rédaction de l'interface

- **Langage métier**, jamais de jargon technique à l'écran (aucun terme de réseau, de stockage, de
  version ni de modèle d'appareil). Préférer « données sur l'appareil », « en attente d'envoi »,
  « connexion sécurisée », « synchronisé ».
- **Aucun code interne affiché** : ni référence d'exigence, ni code de règle de gestion, ni code
  interne de rôle. Ces codes servent au suivi, pas à l'interface.
- **Pas de surpromesse** : ne pas qualifier un document d'« immuable », « infalsifiable » ou
  « certifié ». Formuler sobrement : « horodaté », « tracé », « non modifiable », « empreinte
  d'intégrité ».
- **Statut** toujours porté par icône + libellé.
- **Pas de troncature** du texte essentiel : le texte passe à la ligne.
- **Contexte Côte d'Ivoire** (chantier pilote de Grand-Bassam) et vocabulaire BTP exact (corps
  d'état, bon de livraison, gammes opératoires, etc.).

---

## 9. Cahier des écrans

### 9.1 Application mobile — usage chantier (accès par rôle)

Écrans fonctionnels : connexion hors-ligne, consultation du stock, détail d'un article, saisie
d'une sortie rapide, saisie d'une réception (bon de livraison), déclaration de retour ou de casse,
inventaire tournant, validation des sorties et alertes, historique des mouvements, fiche de route
journalière, détail d'étape et pointage, déclaration de blocage terrain, validation des étapes et
qualité, réaffectation/délégation d'étape, journal de traçabilité, centre de synchronisation et
gestion des conflits.

Accueils dédiés par rôle : Magasinier, Technicien, Chef de chantier, Gestionnaire de stock,
Responsable technique (portée mobile allégée). Chaque accueil n'expose que les fonctions autorisées
au rôle, avec une navigation basse adaptée.

### 9.2 Poste de pilotage web — usage bureau (accès par rôle)

Quinze écrans : connexion, tableau de bord Direction, suivi de l'avancement, journal d'exécution,
tableau de bord stock, référentiel des chantiers et zones, référentiel des magasins, catalogue des
articles, gammes opératoires et corps d'état, paramétrage du chantier et règles de validation,
configuration des seuils de stock, comptes et matrice des droits, supervision des appareils et
révocation, sauvegarde et import des référentiels, affectation des étapes aux équipes.

### 9.3 Cloisonnement des accès

- **Terrain (mobile)** : Magasinier, Technicien, Chef de chantier, Gestionnaire de stock,
  Responsable technique.
- **Bureau (web)** : Direction, Administrateur, Commercial, Acquéreur (lecture seule), Responsable
  technique.
- Chaque plateforme présente **une coquille de navigation unique**, filtrée selon le rôle connecté.
  Une action n'apparaît jamais pour un rôle qui n'y a pas droit.

---

## 10. Principes directeurs

Les règles de gestion structurantes se reflètent dans l'interface : séparation des fonctions (celui
qui réalise une opération ne valide pas sa propre opération), stock négatif autorisé mais signalé
comme anomalie, ajustement de stock uniquement via un inventaire validé, enchaînement des étapes de
travaux par dépendances, expiration automatique d'une session restée trop longtemps sans
synchronisation. La charte est pensée pour rester **modulable** : couleurs, typographie et composants
sont définis comme des éléments réutilisables, partagés entre le web et le mobile.