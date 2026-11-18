"""Métriques d'exploitation (exigence 6.6) et alerte sur rafale d'erreurs.

Le middleware de corrélation appelle ``enregistrer_requete`` à la fin de
chaque requête. ``GET /api/metriques`` rend l'état courant : volume de
requêtes par famille de code de retour, durées, erreurs serveur récentes,
état de la base, dernière exécution de chaque traitement planifié. La route
est protégée par le droit « technique / metriques / LIRE » (posé dans
``configuration/urls.py``, comme pour la documentation de l'API).

Quand le nombre d'erreurs serveur (5xx) atteint ``ALERTES_SEUIL_ERREURS``
dans la fenêtre ``ALERTES_FENETRE_MINUTES`` (5 en 5 minutes par défaut), une
alerte technique part (6.7).

DETTE (v0.2, arbitrage Q-H) : compteurs en mémoire du processus. Ils
repartent de zéro à chaque redémarrage et ne s'additionnent pas entre
processus ; un outil de supervision externe (Prometheus ou celui de la
plateforme) les remplacera.
"""

import threading
import time
from collections import Counter, deque
from typing import Any

from django.conf import settings
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from socle import alertes, sante
from socle.models import ExecutionTraitement


class Compteurs:
    """Compteurs du processus, protégés par un verrou (plusieurs fils
    d'exécution servent les requêtes)."""

    def __init__(self) -> None:
        self._verrou = threading.Lock()
        self.reinitialiser()

    def reinitialiser(self) -> None:
        with self._verrou:
            self.demarre_le = timezone.now()
            self.par_classe: Counter[str] = Counter()
            self.duree_totale_ms = 0.0
            self.duree_max_ms = 0.0
            self.erreurs_recentes: deque[float] = deque()

    def enregistrer(self, statut: int, duree_ms: float, maintenant: float) -> int:
        """Compte la requête ; rend le nombre d'erreurs serveur de la fenêtre."""
        fenetre = settings.ALERTES_FENETRE_MINUTES * 60
        with self._verrou:
            self.par_classe[f"{statut // 100}xx"] += 1
            self.duree_totale_ms += duree_ms
            self.duree_max_ms = max(self.duree_max_ms, duree_ms)
            if statut >= 500:
                self.erreurs_recentes.append(maintenant)
            while self.erreurs_recentes and self.erreurs_recentes[0] < maintenant - fenetre:
                self.erreurs_recentes.popleft()
            return len(self.erreurs_recentes)

    def instantane(self, maintenant: float) -> dict[str, Any]:
        fenetre = settings.ALERTES_FENETRE_MINUTES * 60
        with self._verrou:
            total = sum(self.par_classe.values())
            recentes = sum(
                1 for instant in self.erreurs_recentes if instant >= maintenant - fenetre
            )
            return {
                "demarre_le": self.demarre_le,
                "requetes": {
                    "total": total,
                    "par_classe": dict(self.par_classe),
                    "duree_moyenne_ms": round(self.duree_totale_ms / total, 1) if total else 0.0,
                    "duree_max_ms": round(self.duree_max_ms, 1),
                },
                "erreurs_serveur_recentes": recentes,
                "fenetre_minutes": settings.ALERTES_FENETRE_MINUTES,
            }


COMPTEURS = Compteurs()


def enregistrer_requete(statut: int, duree_ms: float) -> None:
    """Appelé par le middleware pour chaque requête terminée."""
    erreurs = COMPTEURS.enregistrer(statut, duree_ms, time.monotonic())
    if statut >= 500 and erreurs >= settings.ALERTES_SEUIL_ERREURS:
        alertes.alerter(
            alertes.ERREURS_SERVEUR,
            "Erreurs serveur répétées",
            f"{erreurs} erreurs serveur en moins de {settings.ALERTES_FENETRE_MINUTES} minutes. "
            "Consultez les journaux (champ id_correlation) pour en trouver la cause.",
        )


def dernieres_executions() -> list[ExecutionTraitement]:
    """Dernier passage de chaque traitement (DISTINCT ON de PostgreSQL, servi
    par l'index ``ix_execution_traitement_nom_debut``)."""
    return list(
        ExecutionTraitement.objects.order_by("nom_traitement", "-debut").distinct("nom_traitement")
    )


# --- Point d'entrée -------------------------------------------------------------
class RequetesSerializer(serializers.Serializer):  # type: ignore[type-arg]
    total = serializers.IntegerField()
    par_classe = serializers.DictField(child=serializers.IntegerField())
    duree_moyenne_ms = serializers.FloatField()
    duree_max_ms = serializers.FloatField()


class ExecutionSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    class Meta:
        model = ExecutionTraitement
        fields = ["nom_traitement", "debut", "fin", "statut", "detail"]


class MetriquesSerializer(serializers.Serializer):  # type: ignore[type-arg]
    demarre_le = serializers.DateTimeField()
    requetes = RequetesSerializer()
    erreurs_serveur_recentes = serializers.IntegerField()
    fenetre_minutes = serializers.IntegerField()
    base_de_donnees = serializers.CharField()
    traitements = ExecutionSerializer(many=True)


class VueMetriques(APIView):
    """GET /api/metriques. Le droit exigé est fixé à l'inscription de la
    route (``configuration/urls.py``) : le socle ne dépend d'aucun domaine."""

    @extend_schema(responses=MetriquesSerializer)
    def get(self, request: Request) -> Response:
        base = sante.verifier_base()
        corps = {
            **COMPTEURS.instantane(time.monotonic()),
            "base_de_donnees": base,
            # Base injoignable : les compteurs restent lisibles, pas l'historique.
            "traitements": dernieres_executions() if base == sante.OK else [],
        }
        return Response(MetriquesSerializer(corps).data)
