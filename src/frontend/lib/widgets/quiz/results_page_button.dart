import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:frontend/constants/colors.dart' as appColors;

class ResultsPageButton extends StatelessWidget {
  final VoidCallback? onTap;
  final String text;
  const ResultsPageButton({super.key, this.onTap, required this.text});

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: Alignment.centerLeft,
      child: Padding(
        padding: const EdgeInsets.only(top: 12),
        child: Material(
          borderRadius: BorderRadius.all(Radius.circular(100)),
          color: appColors.primary.withOpacity(1),
          child: InkWell(
            borderRadius: BorderRadius.all(Radius.circular(100)),
            splashColor: appColors.white.withOpacity(0.5),
            onTap: onTap,
            child: Container(
              padding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    text,
                    style: TextStyle(
                      fontFamily: 'NSansM',
                      fontSize: 16, 
                      color: appColors.black
                    ),
                  ),
                  SizedBox(width: 5,),
                  Icon(
                    CupertinoIcons.arrow_right,
                    color: appColors.black,
                    size: 18,
                  )
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}