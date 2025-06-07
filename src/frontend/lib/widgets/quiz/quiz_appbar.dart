import 'package:flutter/material.dart';
import 'package:frontend/widgets/quiz/quiz_appbar_button.dart';

class QuizAppBar extends StatelessWidget {
  const QuizAppBar({super.key});

  @override
  Widget build(BuildContext context) {
    Size size = MediaQuery.of(context).size;
    EdgeInsets dp = MediaQuery.of(context).padding;
    return Container(
      padding: EdgeInsets.fromLTRB(8, dp.top+8, 8, 16),
      height: dp.top + 70,
      // ignore: prefer_const_constructors
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: const [
          Opacity(opacity: 1,child: QuizAppbarButton()),
          Expanded(
            child: Padding(
              padding: EdgeInsets.symmetric(vertical: 8),
              child: FittedBox(
                child: Text(
                  'Finance - India',
                  style: TextStyle(
                    fontFamily: 'NSansB',
                    fontSize: 30,
                  ),
                ),
              ),
            )
          ),
          // SizedBox(width: 20,),
          // QuizAppbarButton(),
          Opacity(opacity: 0,child: QuizAppbarButton()),

        ],
      ),
    );
  }
}

