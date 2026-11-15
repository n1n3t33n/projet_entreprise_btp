import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'components/logo_schiavone.dart';
import 'core/preferences/preferences.dart';
import 'core/providers.dart';
import 'features/auth/domain/etat_auth.dart';
import 'features/auth/presentation/ecran_connexion.dart';
import 'features/auth/presentation/ecran_definition_pin.dart';
import 'features/auth/presentation/ecran_deverrouillage.dart';
import 'features/shell/presentation/coquille.dart';
import 'l10n/traductions.dart';
import 'theme/jetons.dart';
import 'theme/palette.dart';
import 'theme/theme_app.dart';

/// Racine de l'application mobile ChantierSync : thème (clair / sombre) et
/// langue (français, anglais, italien) suivent les préférences de l'opérateur.
class AppChantierSync extends ConsumerWidget {
  const AppChantierSync({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final preferences = ref.watch(preferencesProvider);
    return MaterialApp(
      title: 'ChantierSync',
      debugShowCheckedModeBanner: false,
      theme: ThemeApp.clair(),
      darkTheme: ThemeApp.sombre(),
      themeMode: preferences.theme,
      locale: preferences.langue,
      supportedLocales: languesDisponibles,
      localizationsDelegates: Traductions.localizationsDelegates,
      home: const PorteEntree(),
    );
  }
}

/// Aiguille l'affichage selon l'état d'authentification (EF-AUT-03).
class PorteEntree extends ConsumerStatefulWidget {
  const PorteEntree({super.key});

  @override
  ConsumerState<PorteEntree> createState() => _PorteEntreeState();
}

class _PorteEntreeState extends ConsumerState<PorteEntree> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(controleurAuthProvider.notifier).initialiser();
    });
  }

  @override
  Widget build(BuildContext context) {
    final etat = ref.watch(controleurAuthProvider);
    final (cle, ecran) = switch (etat) {
      AuthInitial() => ('amorce', const _EcranAmorce() as Widget),
      AuthNonConnecte() => ('connexion', const EcranConnexion()),
      AuthEnrolementPin() => ('enrolement', const EcranDefinitionPin()),
      AuthVerrouille(:final profil, :final role, :final derniereConnexion) => (
        'verrou',
        EcranDeverrouillage(
          profil: profil,
          role: role,
          derniereConnexion: derniereConnexion,
        ),
      ),
      AuthDeverrouille(:final profil, :final role) => (
        'ouvert',
        Coquille(profil: profil, role: role),
      ),
    };

    // Changement de section : fondu simple (charte § 7).
    return AnimatedSwitcher(
      duration: context.animationsReduites
          ? Duration.zero
          : Jetons.dureeNormale,
      switchInCurve: Jetons.courbe,
      child: KeyedSubtree(key: ValueKey(cle), child: ecran),
    );
  }
}

/// Écran d'amorçage : la marque, le temps d'ouvrir les données de l'appareil.
class _EcranAmorce extends StatelessWidget {
  const _EcranAmorce();

  @override
  Widget build(BuildContext context) {
    final p = context.palette;
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            LogoSchiavone(hauteur: 84, surPlaque: p.sombre),
            const SizedBox(height: Jetons.espace4),
            const SizedBox(
              width: 22,
              height: 22,
              child: CircularProgressIndicator(strokeWidth: 2.5),
            ),
          ],
        ),
      ),
    );
  }
}
