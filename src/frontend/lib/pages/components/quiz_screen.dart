import 'package:flutter/material.dart';
import 'package:frontend/widgets/quiz/quiz_options.dart';
import 'package:frontend/widgets/quiz/quiz_question.dart';
import 'package:frontend/constants/colors.dart' as appColors;

class QuizScreen extends StatelessWidget {
  const QuizScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
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
        const QuizOptions(),
      ],
    );
  }
}