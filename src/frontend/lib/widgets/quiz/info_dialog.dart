import 'dart:math';

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:frontend/constants/colors.dart' as appColors;
import 'package:frontend/models/quiz_item_model.dart';
import 'package:frontend/providers/quiz_page_provider.dart';
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
                  const SizedBox(height: 12,),
                    Row(
                    children: [
                      Expanded(
                        child: Container(
                          padding: EdgeInsets.symmetric(horizontal: 8, vertical: 8),
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.all(Radius.circular(12.5)),
                            border: Border.all(width: 1, color: appColors.white)
                          ),
                          child: Text(
                            data.options[data.correctAnswerIndex],
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              fontFamily: 'NSansM',
                              color: appColors.white,
                              fontSize: 16
                            ),
                          ),
                        ),  
                      ),
                      SizedBox(width: 8,),
                      Icon(CupertinoIcons.checkmark_alt, color: appColors.green,)
                    ],
                  ),
                  const SizedBox(height: 12,),

                  provider.selectedOption-1 != data.correctAnswerIndex?
                  Padding(
                    padding: EdgeInsets.only(bottom: 12),
                    child: Row(
                      children: [
                        Expanded(
                          child: Container(
                            padding: EdgeInsets.symmetric(horizontal: 8, vertical: 8),
                            decoration: BoxDecoration(
                              borderRadius: BorderRadius.all(Radius.circular(12.5)),
                              border: Border.all(width: 1, color: appColors.white)
                            ),
                            child: Text(
                              data.options[max(1, provider.selectedOption)-1],
                              textAlign: TextAlign.center,
                              style: TextStyle(
                                fontFamily: 'NSansM',
                                color: appColors.white,
                                fontSize: 16
                              ),
                            ),
                          ),  
                        ),
                        SizedBox(width: 12,),
                        Icon(CupertinoIcons.clear, color: appColors.red, size: 18,)
                      ],
                    ),
                  ) : SizedBox.shrink(),
                  Text(
                    data.explanation,
                    style: TextStyle(
                      color: appColors.white,
                      fontFamily: 'NSansL',
                      fontSize: 18
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