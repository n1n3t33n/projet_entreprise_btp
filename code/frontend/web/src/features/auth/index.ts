/*
  Point d'entrée public du module authentification. Le routeur n'importe que
  `PageConnexion` ; la couche d'accès est consommée par `app/SessionProvider`
  et par l'écran d'administration des comptes.
*/

export { PageConnexion } from '@/features/auth/pages/PageConnexion'
