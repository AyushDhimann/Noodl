import 'package:flutter/material.dart';
import 'package:frontend/constants/colors.dart' as appColors;

class QuizAnswerItem extends StatelessWidget {
  final bool selected;
  final String text;
  final int uid;
  final VoidCallback onTap;
  const QuizAnswerItem({super.key, required this.selected, required this.text, required this.uid, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(12, 0, 12, 18),
      child: InkWell(
        onTap: onTap,
        borderRadius: const BorderRadius.all(Radius.circular(12.5)),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          alignment: Alignment.center,
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: selected?appColors.primary:null,
            borderRadius: const BorderRadius.all(Radius.circular(12.5)),
            border: selected?null:Border.all(width: 1, color: appColors.white)
          ),
          child: Text(
            text,
            textAlign: TextAlign.center,
            style: TextStyle(
              color: selected? appColors.black : appColors.white,
              fontFamily: 'NSansM',
              fontSize: 18
            ),
          ),
        ),
      ),
    );
  }
}