import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:frontend/constants/colors.dart' as appColors;

class ViewAllNoodlsButton extends StatelessWidget {
  final VoidCallback? onTap;
  final String? text;
  const ViewAllNoodlsButton({super.key, this.onTap, this.text});

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: Alignment.centerRight,
      child: Material(
          color: appColors.primary.withOpacity(0.25),
          borderRadius: BorderRadius.all(Radius.circular(100)),
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.all(Radius.circular(100)),
          child: Container(
            padding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            // decoration: BoxDecoration(
            //   borderRadius: BorderRadius.all(Radius.circular(100)),
            // ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  text??'View All',
                  style: TextStyle(
                    fontFamily: 'NSansM',
                    fontSize: 12,
                    color: appColors.white
                  ),
                ),
                SizedBox(width: 5,),
                Icon(
                  CupertinoIcons.arrow_right,
                  color: appColors.white,
                  size: 15,
                )
              ],
            ),
          ),
        ),
      ),
    );
  }
}