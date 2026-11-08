/*
  Catalogue d'articles — consultation et édition (EF-REF-03).

  Charge les articles enrichis, les catégories et les unités, puis compose le
  gabarit `PageListe` (indicateurs, filtres, tableau). Le filtrage est calculé
  en mémoire sur les lignes déjà chargées ; la création et la modification
  passent par le formulaire en modale, qui déclenche un rechargement.
*/

import { useMemo, useState } from 'react'
import { Cube, Package, PencilSimple, Plus, Stack } from '@phosphor-icons/react'
import {
  Button,
  Card,
  type ColonneTable,
  FilterPill,
  Input,
  KpiCard,
  StatusPill,
  Table,
} from '@/components/ui'
import { PageListe } from '@/components/templates'
import { listerArticles, listerCategories, listerUnites } from '@/features/referentiels/api'
import { FormulaireArticle } from '@/features/referentiels/pages/FormulaireArticle'
import { useRequete } from '@/lib/hooks/useRequete'
import { libelleOrigine, libelleTypeUnite, tonActif } from '@/features/referentiels/presentation/libelles'
import type { ArticleVue } from '@/features/referentiels/types'

type FiltreActif = 'tous' | 'actifs' | 'inactifs'

export type CatalogueArticlesProps = {
  peutEditer: boolean
}

function sansAccents(valeur: string): string {
  return valeur
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .toLowerCase()
}

export function CatalogueArticles({ peutEditer }: CatalogueArticlesProps) {
  const articlesEtat = useRequete(listerArticles, [])
  const categoriesEtat = useRequete(listerCategories, [])
  const unitesEtat = useRequete(listerUnites, [])

  const [recherche, setRecherche] = useState('')
  const [codeCategorie, setCodeCategorie] = useState('toutes')
  const [filtreActif, setFiltreActif] = useState<FiltreActif>('tous')

  const [modaleOuverte, setModaleOuverte] = useState(false)
  const [articleEdite, setArticleEdite] = useState<ArticleVue | null>(null)

  const articles = useMemo(() => articlesEtat.donnees ?? [], [articlesEtat.donnees])
  const categories = useMemo(() => categoriesEtat.donnees ?? [], [categoriesEtat.donnees])
  const unites = useMemo(() => unitesEtat.donnees ?? [], [unitesEtat.donnees])

  const lignesFiltrees = useMemo(() => {
    const terme = sansAccents(recherche.trim())
    return articles.filter((article) => {
      if (codeCategorie !== 'toutes' && article.codeCategorie !== codeCategorie) {
        return false
      }
      if (filtreActif === 'actifs' && !article.actif) {
        return false
      }
      if (filtreActif === 'inactifs' && article.actif) {
        return false
      }
      if (terme.length > 0) {
        const cible = sansAccents(`${article.code} ${article.designation}`)
        if (!cible.includes(terme)) {
          return false
        }
      }
      return true
    })
  }, [articles, recherche, codeCategorie, filtreActif])

  const indicateurs = useMemo(() => {
    const actifs = articles.filter((article) => article.actif).length
    return { total: articles.length, actifs, inactifs: articles.length - actifs }
  }, [articles])

  function ouvrirCreation() {
    setArticleEdite(null)
    setModaleOuverte(true)
  }

  function ouvrirModification(article: ArticleVue) {
    setArticleEdite(article)
    setModaleOuverte(true)
  }

  const colonnes: ColonneTable<ArticleVue>[] = [
    {
      cle: 'code',
      entete: 'Code',
      largeur: '8rem',
      rendu: (article) => <span className="font-medium text-marine">{article.code}</span>,
      triable: true,
      valeurTri: (article) => article.code,
    },
    {
      cle: 'designation',
      entete: 'Désignation',
      rendu: (article) => article.designation,
      triable: true,
      valeurTri: (article) => article.designation,
    },
    {
      cle: 'categorie',
      entete: 'Catégorie',
      rendu: (article) => article.libelleCategorie,
      triable: true,
      valeurTri: (article) => article.libelleCategorie,
    },
    {
      cle: 'unite',
      entete: 'Unité',
      largeur: '8rem',
      rendu: (article) => article.libelleUnite,
    },
    {
      cle: 'origine',
      entete: 'Origine',
      largeur: '10rem',
      rendu: (article) => libelleOrigine(article.origine),
      triable: true,
      valeurTri: (article) => libelleOrigine(article.origine),
    },
    {
      cle: 'actif',
      entete: 'Statut',
      alignement: 'centre',
      largeur: '7rem',
      rendu: (article) => (
        <StatusPill ton={tonActif(article.actif)} libelle={article.actif ? 'Actif' : 'Inactif'} />
      ),
      triable: true,
      valeurTri: (article) => (article.actif ? 1 : 0),
    },
  ]

  if (peutEditer) {
    colonnes.push({
      cle: 'action',
      entete: '',
      alignement: 'droite',
      largeur: '7rem',
      rendu: (article) => (
        <Button
          variante="discret"
          taille="sm"
          icone={PencilSimple}
          onClick={() => ouvrirModification(article)}
        >
          Modifier
        </Button>
      ),
    })
  }

  const erreur =
    articlesEtat.statut === 'erreur'
      ? articlesEtat.erreur
      : categoriesEtat.statut === 'erreur'
        ? categoriesEtat.erreur
        : unitesEtat.statut === 'erreur'
          ? unitesEtat.erreur
          : null

  if (erreur) {
    return (
      <Card>
        <p className="text-sm text-danger">{erreur}</p>
      </Card>
    )
  }

  const chargement = articlesEtat.statut === 'chargement' || articlesEtat.statut === 'attente'

  return (
    <>
      <PageListe
        titre="Catalogue d'articles"
        description="Référentiel des articles consommés sur les chantiers"
        lectureSeule={!peutEditer}
        actions={
          peutEditer ? (
            <Button variante="primaire" icone={Plus} onClick={ouvrirCreation}>
              Nouvel article
            </Button>
          ) : undefined
        }
        indicateurs={
          <>
            <KpiCard libelle="Articles" valeur={indicateurs.total} icone={Package} accent="marine" />
            <KpiCard libelle="Actifs" valeur={indicateurs.actifs} icone={Cube} accent="succes" />
            <KpiCard libelle="Catégories" valeur={categories.length} icone={Stack} accent="sarcelle" />
          </>
        }
        filtres={
          <>
            <Input
              type="search"
              aria-label="Rechercher un article"
              placeholder="Rechercher un code ou une désignation…"
              value={recherche}
              onChange={(evenement) => setRecherche(evenement.target.value)}
              className="max-w-xs"
            />

            <select
              aria-label="Filtrer par catégorie"
              value={codeCategorie}
              onChange={(evenement) => setCodeCategorie(evenement.target.value)}
              className="h-10 rounded-controle border border-bordure bg-surface px-3 text-sm text-texte focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sarcelle"
            >
              <option value="toutes">Toutes les catégories</option>
              {categories.map((categorie) => (
                <option key={categorie.code} value={categorie.code}>
                  {categorie.libelle}
                </option>
              ))}
            </select>

            <span className="mx-1 h-6 w-px bg-bordure" aria-hidden />

            <FilterPill
              libelle="Tous"
              actif={filtreActif === 'tous'}
              onBasculer={() => setFiltreActif('tous')}
            />
            <FilterPill
              libelle="Actifs"
              actif={filtreActif === 'actifs'}
              onBasculer={() => setFiltreActif('actifs')}
            />
            <FilterPill
              libelle="Inactifs"
              actif={filtreActif === 'inactifs'}
              onBasculer={() => setFiltreActif('inactifs')}
            />
          </>
        }
      >
        <Table
          intitule="Articles du catalogue"
          colonnes={colonnes}
          lignes={lignesFiltrees}
          cleLigne={(article) => article.id}
          chargement={chargement}
          triInitial={{ cle: 'code', sens: 'asc' }}
          parPage={12}
          hauteurMax="40rem"
          messageVide="Aucun article ne correspond aux filtres."
        />

        {/* Référentiels secondaires affichés en lecture : leur édition relève
            d'EF-REF-04 (unités) et d'une gestion des catégories, prévues dans
            une étape ultérieure. */}
        <Card titre="Unités de mesure" icone={Cube} className="mt-6">
          <ul className="flex flex-wrap gap-2">
            {unites.map((unite) => (
              <li
                key={unite.code}
                className="rounded-controle border border-bordure bg-fond px-3 py-1.5 text-sm text-texte"
              >
                {unite.libelle}{' '}
                <span className="text-texte-secondaire">· {libelleTypeUnite(unite.typeUnite)}</span>
              </li>
            ))}
          </ul>
        </Card>
      </PageListe>

      {peutEditer && (
        <FormulaireArticle
          ouvert={modaleOuverte}
          onFermer={() => setModaleOuverte(false)}
          article={articleEdite}
          categories={categories}
          unites={unites}
          onEnregistre={() => articlesEtat.recharger()}
        />
      )}
    </>
  )
}
