import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:frontend/constants/colors.dart' as appColors;

class QuizAppbarButton extends StatelessWidget {
  const QuizAppbarButton({super.key});

  @override
  Widget build(BuildContext context) {
    return Material(
      color: appColors.secondary,
      borderRadius: const BorderRadius.all(Radius.circular(12.5)),
      child: InkWell(
        onTap: (){},
        borderRadius: const BorderRadius.all(Radius.circular(10)),
        child: Container(
          width: 45,
          height: 45,
          alignment: Alignment.center,
          child: Icon(
            CupertinoIcons.clear,
            size: 24,
            color: appColors.white,
          ),
        ),
      ),
    );
  }
}