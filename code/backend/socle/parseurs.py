"""Lecture de corps JSON compressés (ENF-02 : « envoi par lots, compressé »).

Le téléphone peut envoyer ses lots en gzip (``Content-Encoding: gzip``) pour
économiser la connexion du chantier. Le corps décompressé est borné : une
petite archive qui se déploierait en gigaoctets (« bombe gzip ») est refusée.
"""

import io
import zlib
from collections.abc import Mapping
from typing import Any

from rest_framework.exceptions import ParseError
from rest_framework.parsers import JSONParser


class JSONCompressible(JSONParser):
    """JSON, éventuellement compressé en gzip."""

    taille_max = 5_000_000  # octets décompressés

    def parse(
        self,
        stream: Any,
        media_type: str | None = None,
        parser_context: Mapping[str, Any] | None = None,
    ) -> Any:
        requete = (parser_context or {}).get("request")
        encodage = requete.META.get("HTTP_CONTENT_ENCODING", "") if requete is not None else ""
        if encodage.lower() != "gzip":
            return super().parse(stream, media_type, parser_context)
        decompresseur = zlib.decompressobj(16 + zlib.MAX_WBITS)
        try:
            brut = decompresseur.decompress(stream.read(), self.taille_max + 1)
        except zlib.error as erreur:
            raise ParseError("Le corps compressé est illisible.") from erreur
        if len(brut) > self.taille_max or decompresseur.unconsumed_tail:
            raise ParseError("Le lot décompressé est trop volumineux.")
        return super().parse(io.BytesIO(brut), media_type, parser_context)
