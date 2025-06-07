import 'package:flutter/material.dart';
import 'package:frontend/widgets/quiz/quiz_appbar.dart';
// ignore: library_prefixes
import 'package:frontend/constants/colors.dart' as appColors;
import 'package:frontend/widgets/quiz/quiz_options.dart';
import 'package:frontend/widgets/quiz/quiz_question.dart';

class QuizPage extends StatelessWidget {
  const QuizPage({super.key});

  @override
  Widget build(BuildContext context) {
    // ignore: unused_local_variable
    Size size = MediaQuery.of(context).size;
    EdgeInsets dp = MediaQuery.of(context).padding;
    // ignore: prefer_const_constructors
    return Scaffold(
      backgroundColor: appColors.bgColor,
      body:  Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const QuizAppBar(),
          LinearProgressIndicator(
            value: 0.8,
            color: appColors.accent,
          ),
          const QuizQuestion(text: 'What is the full form of UPI, a widely used digital payment system in India?',),
          Padding(
            padding: const EdgeInsets.fromLTRB(12, 0, 12, 8),
            child: Text(
              'Select one',
              style: TextStyle(
                fontFamily: 'NSansM',
                color: appColors.white.withOpacity(0.5)
              ),
            ),
          ),
          const QuizOptions()
        ],
      ),
    );
  }
}