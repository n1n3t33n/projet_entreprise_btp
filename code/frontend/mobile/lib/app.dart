import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'core/providers.dart';
import 'features/auth/domain/etat_auth.dart';
import 'features/auth/presentation/ecran_connexion.dart';
import 'features/auth/presentation/ecran_definition_pin.dart';
import 'features/auth/presentation/ecran_deverrouillage.dart';
import 'features/shell/presentation/coquille.dart';
import 'theme/theme_app.dart';

/// Racine de l'application mobile ChantierSync.
class AppChantierSync extends StatelessWidget {
  const AppChantierSync({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'ChantierSync',
      debugShowCheckedModeBanner: false,
      theme: ThemeApp.clair(),
      locale: const Locale('fr'),
      supportedLocales: const [Locale('fr')],
      localizationsDelegates: const [
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
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
    return switch (etat) {
      AuthInitial() => const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      ),
      AuthNonConnecte() || AuthVerrouExpire() => const EcranConnexion(),
      AuthEnrolementPin() => const EcranDefinitionPin(),
      AuthVerrouille(:final identifiant) => EcranDeverrouillage(
        identifiant: identifiant,
      ),
      AuthDeverrouille(:final role) => Coquille(role: role),
    };
  }
}
