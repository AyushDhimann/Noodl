import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:frontend/constants/colors.dart' as appColors;

class GenerateButton extends StatelessWidget {
  final VoidCallback? onTap;
  const GenerateButton({super.key, this.onTap});

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: Alignment.centerRight,
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
                  'Generate',
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
    );
  }
}