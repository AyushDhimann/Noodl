import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:frontend/constants/colors.dart' as appColors;


class InfoDialogOptionDisplay extends StatelessWidget {
  final String text;
  final bool correct;
  const InfoDialogOptionDisplay({super.key, required this.text, required this.correct});

  @override
  Widget build(BuildContext context) {
    return                   Padding(
      padding: const EdgeInsets.only(bottom: 12,),
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
                text,
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontFamily: 'NSansM',
                  color: appColors.white,
                  fontSize: 16
                ),
              ),
            ),  
          ),
          // SizedBox(width: 12,), for incorrect
          SizedBox(width: correct?8:12,),
          correct?
          Icon(CupertinoIcons.checkmark_alt, color: appColors.green,)
            :Icon(CupertinoIcons.clear, color: appColors.red, size: 18,)

        ],
      ),
    );
  }
}