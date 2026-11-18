#!/usr/bin/env python
"""Point d'entrée des commandes Django du backend ChantierSync.

Les réglages par défaut sont ceux du développement ; la production et les
tests choisissent les leurs via ``DJANGO_SETTINGS_MODULE``.
"""

import os
import sys


def main() -> None:
    """Lance la commande Django demandée sur la ligne de commande."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configuration.reglages.developpement")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
