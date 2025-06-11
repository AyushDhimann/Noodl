import 'package:flutter/material.dart';
import 'package:frontend/models/quiz_item_model.dart';
import 'package:frontend/providers/quiz_page_provider.dart';
import 'package:frontend/widgets/quiz/info_dialog.dart';
import 'package:frontend/widgets/quiz/quiz_options.dart';
import 'package:frontend/widgets/quiz/quiz_question.dart';
import 'package:frontend/constants/colors.dart' as appColors;
import 'package:frontend/widgets/quiz/question_submit_button.dart';
import 'package:provider/provider.dart';

class QuizScreen extends StatelessWidget {
  final QuizItemModel data;
  const QuizScreen({super.key, required this.data});

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            QuizQuestion(text: data.question,),
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
            QuizOptions(data: data,),
          ],
        ),
        Column(
          mainAxisAlignment: MainAxisAlignment.end,
          children: [
            Consumer<QuizPageProvider>(
              builder: (ccontext, provider, child) => 
                IgnorePointer(
                  // ignoring: provider.selectedOption==0,
                  ignoring: false,
                  child: QuestionSubmitButton(
                    "Submit",
                    currentquiz: data,
                    isActive: provider.selectedOption!=0,
                    onTap: ()=>showInfoDialog(context, data: data),
                  ),
                )
            ),
          ],
        )
      ],
    );
  }
}