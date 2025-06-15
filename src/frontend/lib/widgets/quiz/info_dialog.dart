import 'dart:math';

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:frontend/constants/colors.dart' as appColors;
import 'package:frontend/models/quiz_item_model.dart';
import 'package:frontend/providers/quiz_page_provider.dart';
import 'package:frontend/widgets/quiz/option_display_info_dialog.dart';
import 'package:frontend/widgets/quiz/quiz_answer_item.dart';
import 'package:frontend/widgets/quiz/question_submit_button.dart';
import 'package:provider/provider.dart';

void showInfoDialog(BuildContext context, {required QuizItemModel data}){
  Size size = MediaQuery.of(context).size;
  EdgeInsets dp = MediaQuery.of(context).padding;
  // bool isCorrectOption = Provider.of<QuizPageProvider>(context).selectedOption -1 == data.correctAnswerIndex;
  showGeneralDialog(
    context: context,
    barrierColor: appColors.black.withOpacity(0.9),
    pageBuilder: (context, animation, secondaryAnimation) {
      // KINDLY REMOVE THIS BITCCCHHH
      return Scaffold(
        backgroundColor: Colors.transparent,
        body: Consumer<QuizPageProvider>(
          builder: (context, provider, child) =>
          Center(
            child: Container(
              width: size.width - 24,
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                borderRadius: const BorderRadius.all(Radius.circular(18)),
                color: appColors.grey
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  Text(
                    provider.selectedOption-1 == data.correctAnswerIndex?
                      'You\'re Correct!'
                        :'Wrong Answer!',
                    style: TextStyle(
                      fontFamily: 'NSansM',
                      color: appColors.white,
                      fontSize: 22
                    ),
                  ),
                  SizedBox(height: 12,),

                  provider.selectedOption-1 != data.correctAnswerIndex?
                    InfoDialogOptionDisplay(text: data.options[max(1, provider.selectedOption)-1], correct: false)
                      : SizedBox.shrink(),
                  
                  InfoDialogOptionDisplay(text: data.options[data.correctAnswerIndex], correct: true),

                                    SizedBox(
                    width: size.width-48,
                    child: SingleChildScrollView(
                      child: Markdown(
                        data: data.explanation,
                        padding: EdgeInsets.zero,
                        physics: NeverScrollableScrollPhysics(),
                        shrinkWrap: true,
                        styleSheet: MarkdownStyleSheet(
                          h2: TextStyle(
                            fontFamily: 'NSansB',
                            fontSize: 22,
                            color: appColors.white,
                          ),
                          h1: TextStyle(
                            fontFamily: 'NSansB',
                            fontSize: 22,
                            color: appColors.white,
                          ),
                          h3: TextStyle(
                            fontFamily: 'NSansB',
                            fontSize: 22,
                            color: appColors.white,
                          ),
                          p: TextStyle(
                            fontFamily: 'NSansL',
                            fontSize: 18,
                            color: appColors.white,
                            // backgroundColor: appColors.black,
                          ),
                          strong: TextStyle(
                            fontFamily: 'NSansB',
                            fontSize: 18,
                            color: appColors.white,
                          ),
                          code: TextStyle(fontFamily: 'MonolisaRI', fontSize: 16),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 20,),
                  
                  // continue button
                  Material(
                      color: appColors.white,
                      borderRadius: const BorderRadius.all(Radius.circular(100)),
                      child: InkWell(
                        onTap: () async{
                          Navigator.of(context).pop();
                          await Future.delayed(Duration(milliseconds: 150));
                          provider.goToNextQues();
                        },
                        borderRadius: const BorderRadius.all(Radius.circular(100)),
                        child: Container(
                          width: double.infinity,
                          padding: const EdgeInsets.all(12),
                          alignment: Alignment.center,
                          child: Text(
                            'Continue',
                            style: TextStyle(
                              color: appColors.bgColor,
                              fontFamily: 'NSansM',
                              fontSize: 18
                            ),
                          ),
                        ),
                      ),
                    ),
                ],  
              ),
            ),
          ),
        ),
      );
    },
  );
}


