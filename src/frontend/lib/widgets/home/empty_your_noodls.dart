import 'package:flutter/material.dart';
import 'package:frontend/constants/colors.dart' as appColors;

class EmptyYourNoodls extends StatelessWidget {
  final String? text;
  const EmptyYourNoodls({super.key, this.text});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Container(
        height: 150,
        width: 200,
        alignment: Alignment.center,
        child: Text(
          text??'No noodls yet! Start by generating one or picking from the community.',
          textAlign: TextAlign.center,
          style: TextStyle(
            color: appColors.white.withOpacity(0.35),
            fontFamily: 'NSansL',
            fontSize: 15,
          ),
        ),
      ),
    );
  }
}