import 'package:flutter/material.dart';
import 'package:frontend/constants/colors.dart' as appColors;

class HeadingWidget extends StatelessWidget {
  final String heading;
  final String subHeading;
  const HeadingWidget({super.key, required this.heading, required this.subHeading});

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          heading,
          style: TextStyle(
            color: appColors.white,
            fontFamily: 'NSansB',
            fontSize: 22
          ),
        ),
        SizedBox(height: 5,),
        Text(
          subHeading,
          style: TextStyle(
            color: appColors.white.withOpacity(0.5),
            fontFamily: 'NSansM',
            fontSize: 12
          ),
        ),
        SizedBox(height: 12,),
      ],
    );
  }
}