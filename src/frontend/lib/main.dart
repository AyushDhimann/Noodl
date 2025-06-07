import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:frontend/pages/quiz.dart';
import 'package:frontend/providers/quiz_page_provider.dart';
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
        ChangeNotifierProvider(create: (context) => QuizPageProvider(),)
      ],
      child: MaterialApp(
        debugShowCheckedModeBanner: false,
        theme: ThemeData.dark(
          useMaterial3: true
        ),
        // ignore: prefer_const_constructors
        home: QuizPage(),
      ),
    );
  }
}