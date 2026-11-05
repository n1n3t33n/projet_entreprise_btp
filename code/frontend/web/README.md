# ChantierSync — Poste de pilotage web

Interface web de supervision de ChantierSync, la solution de gestion de chantier
d'Italia Construction (groupe Schiavone). Application monopage découplée, consommant
l'API Django REST du projet.

## Pile technique

- React 18 + TypeScript
- Vite (serveur de développement et build)
- Tailwind CSS (thème dérivé de la charte graphique)
- React Router (navigation)
- Axios (couche d'accès aux données)

## Démarrage

```bash
npm install
cp .env.example .env   # ajuster l'URL de l'API si nécessaire
npm run dev
```

Le serveur de développement démarre sur http://localhost:5173.

## Scripts

| Script             | Rôle                                            |
| ------------------ | ----------------------------------------------- |
| `npm run dev`      | Serveur de développement avec rechargement à chaud |
| `npm run build`    | Vérification des types puis build de production |
| `npm run preview`  | Prévisualisation du build de production         |
| `npm run lint`     | Analyse statique (ESLint)                       |
| `npm run format`   | Formatage du code (Prettier)                    |

## Structure

```
src/
  app/                  Composition de l'application
  routes/               Définition de la navigation
  config/               Navigation et paramètres réglables de l'application
  components/ui/        Bibliothèque de composants d'interface réutilisables
  components/templates/ Gabarits de page partagés entre les modules
  features/             Modules métier (auth, dashboard, avancement, stock,
                        referentiels, admin, synchronisation, acquereur)
  lib/                  Règles de gestion et utilitaires transverses
  lib/api/              Client HTTP et couche d'accès aux données
  lib/mocks/            Adaptateur de simulation
  types/                Modèles de données partagés
  theme/                Jetons de style dérivés de la charte
```

## Pages de référence

Deux écrans servent de référence pendant le développement. Ils ne font pas partie
du parcours utilisateur et ne figurent pas dans la navigation.

| Chemin           | Contenu                                                       |
| ---------------- | ------------------------------------------------------------- |
| `/design-system` | Couleurs, typographie, rayons, élévations et iconographie      |
| `/ui-kit`        | Tous les composants d'interface et le gabarit de page partagé  |

## Conventions d'interface

Les composants de `components/ui` ne contiennent aucune donnée métier : tout leur
contenu arrive par leurs propriétés, ce qui leur permet de servir indifféremment le
module stock, le module avancement ou l'espace acquéreur. Les écrans destinés à un
rôle consultant réutilisent les mêmes composants et le même gabarit, avec la
propriété `lectureSeule`, plutôt qu'une seconde version de l'écran.

Les valeurs de style vivent toutes dans `src/index.css` : couleurs, rayons, ombres,
durées et courbes d'animation. Les composants s'y réfèrent par des classes
utilitaires et n'écrivent jamais une valeur en dur. Seules les propriétés
`transform` et `opacity` sont animées, et la préférence système de mouvement
réduit ramène l'affichage à son état final immédiatement.

## Paramètres réglables

Tout ce qui relève d'un choix d'exploitation plutôt que d'un choix de style est
déclaré dans `src/config/parametres.ts` : fréquence des rappels d'alerte par
degré d'urgence, rôles destinataires par degré d'urgence, escalade, canaux de
diffusion, durée d'affichage des notifications, et facteur de pré-remplissage du
seuil de confort. Aucun composant ne lit ce fichier. Un écran ou un fournisseur
le consulte et transmet la valeur par propriété, de sorte qu'un composant reste
réutilisable dans un contexte où le paramètre serait différent.

Le seuil de confort d'un article est une donnée du référentiel, portée par
l'article lui-même. Le facteur déclaré dans les paramètres ne s'y substitue pas :
il pré-remplit le champ à la création d'une fiche, et sert de repli d'affichage
pour une fiche antérieure au champ. Les destinataires des alertes sont choisis
par rôle depuis l'écran d'administration ; les adresses viennent du compte de
chaque utilisateur et ne sont jamais recopiées dans la configuration.

L'escalade est une option, inactive par défaut et activable depuis
l'administration. Quand elle est active, une alerte restée sans suite après un
nombre configurable de rappels part aussi vers les rôles d'escalade, qui
s'ajoutent aux destinataires habituels sans les remplacer.

Ces valeurs s'appliquent tant que l'API ne sert pas la configuration de
l'entreprise. Elles sont destinées à être remplacées par la réponse de l'endpoint
de paramétrage, puis à devenir modifiables depuis l'écran d'administration.

## Règles de gestion partagées

`src/lib/seuils.ts` porte le classement d'un stock par rapport à ses seuils :
vide à l'épuisement, critique sous le seuil d'alerte, mini dès que le seuil
d'alerte est atteint, plein au-delà du seuil de confort. Un stock n'est jamais
négatif ; une quantité inférieure ou égale à zéro est un stock vide. Le fichier
expose aussi le degré d'urgence associé à chaque niveau, qui sert de clé aux
paramètres d'alerte. Ces fonctions sont séparées des composants pour servir aussi
bien à l'affichage qu'au tri, au filtrage et au déclenchement des rappels.

## Configuration

Les données métier ne sont jamais écrites dans les composants : elles transitent
par la couche d'accès (`lib/api`). En l'absence d'API disponible, l'adaptateur de
simulation (`lib/mocks`) répond aux mêmes appels. Le basculement entre simulation
et API réelle se fait via `VITE_USE_MOCKS`, sans modifier les composants.
