import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:frontend/constants/colors.dart' as appColors;

class GenerateButton extends StatelessWidget {
  final VoidCallback? onTap;
  final String? text;
  final bool altStyling;
  const GenerateButton({super.key, this.onTap, this.text, this.altStyling=false});

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: Alignment.centerRight,
      child: Material(
        borderRadius: BorderRadius.all(Radius.circular(100)),
        color: appColors.primary.withOpacity(altStyling?0:1),
        child: InkWell(
          borderRadius: BorderRadius.all(Radius.circular(100)),
          splashColor: appColors.white.withOpacity(0.5),
          onTap: onTap,
          child: Container(
            padding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: altStyling? BoxDecoration(
              border: Border.all(width: 1, color: appColors.primary),
              borderRadius: BorderRadius.all(Radius.circular(100)),
            ):null,
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  text??'Generate',
                  style: TextStyle(
                    fontFamily: 'NSansM',
                    fontSize: 16, 
                    color: altStyling?appColors.white: appColors.black
                  ),
                ),
                SizedBox(width: 5,),
                Icon(
                  CupertinoIcons.arrow_right,
                  color: altStyling?appColors.white: appColors.black,
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