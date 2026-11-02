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
  app/            Composition de l'application
  routes/         Définition de la navigation
  components/ui/  Composants d'interface réutilisables
  features/       Modules métier (auth, dashboard, avancement, stock,
                  referentiels, admin, synchronisation, acquereur)
  lib/api/        Client HTTP et couche d'accès aux données
  lib/mocks/      Adaptateur de simulation
  types/          Modèles de données partagés
  theme/          Jetons de style dérivés de la charte
```

## Configuration

Les données métier ne sont jamais écrites dans les composants : elles transitent
par la couche d'accès (`lib/api`). En l'absence d'API disponible, l'adaptateur de
simulation (`lib/mocks`) répond aux mêmes appels. Le basculement entre simulation
et API réelle se fait via `VITE_USE_MOCKS`, sans modifier les composants.
