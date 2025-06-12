import 'package:flutter/material.dart';
import 'package:frontend/constants/colors.dart' as appColors;
import 'package:frontend/models/quiz_item_model.dart';

class QuestionSubmitButton extends StatelessWidget {
  final String text;
  final VoidCallback? onTap;
  final bool isActive;
  final QuizItemModel currentQuizItem;
  const QuestionSubmitButton(this.text, {super.key, this.onTap, required this.isActive, required this.currentQuizItem,});

  @override
  Widget build(BuildContext context) {
    EdgeInsets dp = MediaQuery.of(context).padding;
    return Padding(
      padding: EdgeInsets.fromLTRB(12, 0, 12, dp.bottom + 12),
      child: AnimatedOpacity(
        duration: const Duration(milliseconds: 200),
        opacity: isActive?1:0,
        child: Material(
          color: appColors.white,
          borderRadius: const BorderRadius.all(Radius.circular(100)),
          child: InkWell(
            onTap: isActive?onTap:null,
            borderRadius: const BorderRadius.all(Radius.circular(100)),
            child: Container(
              alignment: Alignment.center,
              padding: const EdgeInsets.all(12),
              child: Text(
                text,
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: appColors.black,
                  fontFamily: 'NSansM',
                  fontSize: 18
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}