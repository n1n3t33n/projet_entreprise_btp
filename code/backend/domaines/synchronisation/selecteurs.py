"""Lectures du domaine synchronisation."""

from typing import Any

from domaines.synchronisation.models import LotSynchronisation


def lot(id_lot: Any) -> LotSynchronisation:
    """Un lot et ses résultats (rapprochés par ``uuid_evenement``, ET-3)."""
    return LotSynchronisation.objects.prefetch_related("resultats").get(pk=id_lot)
