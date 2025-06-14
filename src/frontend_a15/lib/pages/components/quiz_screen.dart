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
        SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              QuizQuestion(text: data.question),
              Padding(
                padding: const EdgeInsets.fromLTRB(12, 0, 12, 8),
                child: Text(
                  'Select one',
                  style: TextStyle(
                    fontFamily: 'NSansM',
                    color: appColors.white.withOpacity(0.5),
                  ),
                ),
              ),
              QuizOptions(data: data),
              // bottom padding + whatver the heigh of the sbimti buttn is
              SizedBox(height: 200,)
            ],
          ),
        ),
        Column(
          mainAxisAlignment: MainAxisAlignment.end,
          children: [
            Consumer<QuizPageProvider>(
              builder: (ccontext, provider, child) => IgnorePointer(
                // ignoring: provider.selectedOption==0,
                ignoring: false,
                child: QuestionSubmitButton(
                  "Submit",
                  // currentQuizItem: data,
                  isActive: provider.selectedOption != 0,
                  onTap: () {
                    provider.increaseQuestionCount();
                    provider.selectedOption - 1 == data.correctAnswerIndex
                        ? provider.increaseScore()
                        : null;
                    showInfoDialog(context, data: data);
                  },
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }
}
