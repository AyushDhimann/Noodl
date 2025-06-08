import 'package:flutter/material.dart';
import 'package:frontend/pages/components/duk.dart';
import 'package:frontend/pages/components/quiz_screen.dart';
import 'package:frontend/providers/quiz_page_provider.dart';
import 'package:frontend/widgets/quiz/info_dialog.dart';
import 'package:frontend/widgets/quiz/quiz_appbar.dart';
// ignore: library_prefixes
import 'package:frontend/constants/colors.dart' as appColors;
// import 'package:frontend/widgets/quiz/quiz_options.dart';
// import 'package:frontend/widgets/quiz/quiz_question.dart';
import 'package:frontend/widgets/quiz/quiz_submit_button.dart';
import 'package:provider/provider.dart';

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
      body:  Consumer<QuizPageProvider>(
        builder: (context, provider, child) => 
        
        Stack(
          children: [
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const QuizAppBar(),
                SizedBox(
                  height: 2,
                  child: LinearProgressIndicator(
                    value: provider.progress/8,
                    color: appColors.accent,
                  ),
                ),
                SizedBox(
                  width: size.width,
                  height: size.height - dp.top -70 -2,
                  child: PageView(
                    controller: provider.quizQuesContoller,
                    children: const [
                      QuizScreen(),
                      DidYouKnowScreen(),
                      QuizScreen(),
                      DidYouKnowScreen(),
                      QuizScreen(),
                      DidYouKnowScreen(),
                      QuizScreen(),
                      DidYouKnowScreen(),
                      QuizScreen(),
                      DidYouKnowScreen(),
                      QuizScreen(),
                      DidYouKnowScreen(),
                      QuizScreen(),
                      DidYouKnowScreen(),
                      QuizScreen(),
                    ],
                  ),
                )
              ],
            ),
            Column(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                Consumer<QuizPageProvider>(
                  builder: (ccontext, provider, child) => 
                    QuizSubmitButton(
                      "Submit",
                      isActive: provider.selectedOption!=0,
                      onTap: ()=>showInfoDialog(context),
                  )
                ),
              ],
            )
          ],
        ),
      ),
    );
  }
}