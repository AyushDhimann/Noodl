import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:frontend/pages/home.dart';
import 'package:frontend/pages/login.dart';
import 'package:frontend/pages/onboarding_page.dart';
import 'package:frontend/pages/quiz.dart';
import 'package:frontend/providers/generate_page_provider.dart';
import 'package:frontend/providers/metamask_provider.dart';
import 'package:frontend/providers/search_page_provider.dart';
import 'package:frontend/providers/quiz_page_provider.dart';
import 'package:frontend/services/services.dart';
import 'package:provider/provider.dart';
import 'constants/colors.dart' as appColors;

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    // Set status bar style
    SystemChrome.setSystemUIOverlayStyle(SystemUiOverlayStyle.light);
    SystemChrome.setSystemUIOverlayStyle(
      const SystemUiOverlayStyle(statusBarColor: Colors.transparent),
    );

    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => QuizPageProvider()),
        ChangeNotifierProvider(create: (_) => GeneratePageProvider()),
        ChangeNotifierProvider(create: (_) => MetaMaskProvider()),
        ChangeNotifierProvider(create: (_) => SearchPageProvider()),
      ],
      child: MaterialApp(
        debugShowCheckedModeBanner: false,
        theme: ThemeData.dark(useMaterial3: true),
        home: Consumer<MetaMaskProvider>(
          builder: (context, provider, _) {
            if (provider.isConnected) {
              return FutureBuilder<dynamic>(
                future: APIservice.fetchUserNameCountry(walletAdd: provider.walletAddress!),
                builder: (context, snapshot) {
                  if (snapshot.connectionState == ConnectionState.waiting) {
                    return Scaffold(
                      backgroundColor: appColors.bgColor,
                      body: const Center(child: CupertinoActivityIndicator()),
                    );
                  } else if (snapshot.hasData && snapshot.data!['id'] != null) {
                    return const HomePage();
                  } else {
                    return const OnboardingPage();
                  }
                },
              );
            } else {
              return const LoginPage();
            }
          },
        ),
      ),
    );
  }
}
