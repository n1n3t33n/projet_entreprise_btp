"""Le contrat committé (contrat/openapi.yaml) correspond au code (Q14).

Si ce test échoue, l'API a changé sans que le contrat soit régénéré et relu :
lancer « python manage.py spectacular --file contrat/openapi.yaml --validate »
puis faire relire le diff aux fronts.
"""

from io import StringIO
from pathlib import Path

from django.conf import settings
from django.core.management import call_command

CONTRAT = Path(settings.RACINE) / "contrat"


def test_le_contrat_committe_correspond_au_code() -> None:
    sortie = StringIO()
    call_command("spectacular", "--validate", stdout=sortie)
    attendu = (CONTRAT / "openapi.yaml").read_text(encoding="utf-8")
    assert (
        sortie.getvalue().strip() == attendu.strip()
    ), "Le code ne correspond plus à contrat/openapi.yaml : régénérez-le et faites-le relire."
