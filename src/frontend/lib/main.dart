import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:frontend/pages/home.dart';
import 'package:frontend/pages/login.dart';
import 'package:frontend/test/metamasktest.dart';
import 'package:frontend/pages/quiz.dart';
import 'package:frontend/providers/quiz_page_provider.dart';
import 'package:frontend/test/metamask_service.dart';
import 'package:provider/provider.dart';

void main() {

  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    SystemChrome.setSystemUIOverlayStyle(SystemUiOverlayStyle.light);
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (context) => QuizPageProvider(),),
        // ChangeNotifierProvider(create: (context) => MetaMaskProvider(),)
      ],
      child: MaterialApp(
        debugShowCheckedModeBanner: false,
        theme: ThemeData.dark(
          useMaterial3: true
        ),
        // ignore: prefer_const_constructors
        home: QuizPage(),
        // home: HomePage(),
        // ignore: prefer_const_constructors
      //   home: StreamBuilder(
      //   stream: FirebaseAuth.instance.authStateChanges(),
      //   builder: (context, snapshot) {
      //     if(snapshot.hasData){
      //       return const QuizPage();
      //     } else {
      //       return const LoginPage();
      //     }
      //   },
      // ),
        // home: HomePage(),
      ),
    );
  }
}