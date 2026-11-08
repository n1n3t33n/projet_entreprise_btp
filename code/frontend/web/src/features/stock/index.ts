/*
  Point d'entrée public du module stock.

  Les routes importent `@/features/stock` et n'ont besoin que de l'écran
  d'entrée ; le reste (types, api, mocks, écrans internes) est détail
  d'implémentation du module.
*/

export { PageStock } from '@/features/stock/pages/PageStock'
