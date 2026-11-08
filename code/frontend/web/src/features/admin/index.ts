/*
  Point d'entrée public du module administration. Le routeur n'importe que
  `PageAdministration` ; la couche d'accès aux droits est en outre consommée
  par `app/DroitsProvider`, qui alimente toute la coquille.
*/

export { PageAdministration } from '@/features/admin/pages/PageAdministration'
