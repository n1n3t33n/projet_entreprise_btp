"""Signaux émis par le domaine « référentiels ».

Un domaine qui dépend des référentiels s'y abonne dans son ``apps.ready()``
sans que les référentiels le connaissent (la dépendance reste dans un seul
sens) : l'avancement crée les étapes des logements quand une première gamme
devient active pour leur type (RG-A1, EF-AVA-01).
"""

from django.dispatch import Signal

# Émis après la publication d'une version de gamme ; argument : ``gamme``.
gamme_publiee = Signal()
