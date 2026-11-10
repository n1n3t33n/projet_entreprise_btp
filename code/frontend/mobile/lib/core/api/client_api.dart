import 'package:dio/dio.dart';

import '../config/env.dart';

/// Crée le client HTTP partagé, calqué sur le client du web (`lib/api/http.ts`)
/// : même base d'URL, délais explicites, corps JSON. HTTPS imposé par l'URL.
Dio creerDio() {
  return Dio(
    BaseOptions(
      baseUrl: Env.apiBaseUrl,
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 30),
      headers: const {'Content-Type': 'application/json'},
    ),
  );
}
