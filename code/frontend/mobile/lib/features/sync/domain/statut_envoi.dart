/// Statuts d'un événement dans la file d'envoi (ET-3), en `UPPER_SNAKE`.
///
/// `DEJA_RECU` matérialise l'idempotence : si le serveur a déjà intégré
/// l'événement, le rejouer ne crée pas de doublon.
enum StatutEnvoi {
  enAttente('EN_ATTENTE'),
  enCours('EN_COURS'),
  dejaRecu('DEJA_RECU'),
  accepte('ACCEPTE'),
  rejete('REJETE');

  const StatutEnvoi(this.code);

  final String code;

  static StatutEnvoi parCode(String code) {
    for (final statut in StatutEnvoi.values) {
      if (statut.code == code) return statut;
    }
    return StatutEnvoi.enAttente;
  }
}
