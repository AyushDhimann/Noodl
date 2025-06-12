import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:frontend/pages/home.dart';
import 'package:frontend/pages/home.dart';
import 'package:frontend/pages/login.dart';
import 'package:frontend/pages/onboarding_page.dart';
import 'package:frontend/providers/generate_page_provider.dart';
import 'package:frontend/providers/metamask_provider.dart';
import 'package:frontend/services/services.dart';
import 'package:frontend/test/metamasktest.dart';
import 'package:frontend/test/metamasktest.dart';
import 'package:frontend/pages/quiz.dart';
import 'package:frontend/providers/quiz_page_provider.dart';
import 'package:frontend/test/metamask_service.dart';
import 'package:frontend/test/metamask_service.dart';
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
    SystemChrome.setSystemUIOverlayStyle(SystemUiOverlayStyle.light);
    SystemChrome.setSystemUIOverlayStyle(SystemUiOverlayStyle(statusBarColor: Colors.transparent));

    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (context) => QuizPageProvider(),),
        ChangeNotifierProvider(create: (context) => GeneratePageProvider(),),
        ChangeNotifierProvider(create: (context) => MetaMaskProvider(),)
      ],
      child: MaterialApp(
        debugShowCheckedModeBanner: false,
        theme: ThemeData.dark(
          useMaterial3: true
        ),
        // ignore: prefer_const_constructors
        // home: Consumer<MetaMaskProvider>(
        //   builder: (context, provider, child) {
        //     if (provider.isConnected && provider.isOnboardingComplete) {
        //       return const HomePage();
        //     } else if (provider.isConnected && !provider.isOnboardingComplete) {
        //       print(provider.walletAddress);
        //       return FutureBuilder(
        //         future:APIservice.fetchUserNameCountry(walletAdd: provider.walletAddress!),
        //         builder: (context, snapshot) {
        //           if(snapshot.hasData){
        //             if(snapshot.data!['id']!=null){
        //               return HomePage();
        //             } 
        //             return OnboardingPage();
        //           }
        //           return Scaffold(backgroundColor: appColors.bgColor, body: Center(child: CupertinoActivityIndicator())); 
        //         },
        //       );
        //     } else {
        //       return const LoginPage();
        //     }
        //   },
          // builder: (context, provider, child) {
          //   if (provider.isConnected) {
          //     return FutureBuilder(
          //       future: APIservice.fetchUserNameCountry(walletAdd: provider.walletAddress!),
          //       builder: (context, snapshot) {
          //         if(snapshot.hasData){
          //           if(snapshot.data!['id']!=null){
          //             return HomePage();
          //           } 
          //           return OnboardingPage();
          //         }
          //         return Scaffold(backgroundColor: appColors.bgColor, body: Center(child: CupertinoActivityIndicator()));
          //       },
          //     );
          //   } else {
          //     return const LoginPage();
          //   }
          // },
        // ),  
        // ________ TESTING________
        home: HomePage(),
      ),
    );
  }
}