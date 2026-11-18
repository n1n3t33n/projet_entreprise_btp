"""Socle de service technique transverse de ChantierSync (rapport B0 § 6).

Il ne dépend d'aucun domaine métier : journaux, santé, erreurs, limitation du
taux, outils PostgreSQL (partitions, immuabilité). Les domaines s'appuient sur
lui, jamais l'inverse.
"""
