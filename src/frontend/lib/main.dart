import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:frontend/pages/home.dart';
import 'package:frontend/pages/login.dart';
import 'package:frontend/pages/onboarding_page.dart';
import 'package:frontend/providers/metamask_provider.dart';
import 'package:frontend/providers/quiz_page_provider.dart';
import 'package:provider/provider.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    SystemChrome.setSystemUIOverlayStyle(SystemUiOverlayStyle.light);
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (context) => QuizPageProvider()),
        ChangeNotifierProvider(create: (context) => MetaMaskProvider()),
      ],
      child: MaterialApp(
        debugShowCheckedModeBanner: false,
        theme: ThemeData.dark(useMaterial3: true),
        home: Consumer<MetaMaskProvider>(
          builder: (context, provider, child) {
            if (provider.isConnected && provider.isOnboardingComplete) {
              return const HomePage();
            } else if (provider.isConnected && !provider.isOnboardingComplete) {
              return const OnboardingPage();
            } else {
              return const LoginPage();
            }
          },
        ),
      ),
    );
  }
}