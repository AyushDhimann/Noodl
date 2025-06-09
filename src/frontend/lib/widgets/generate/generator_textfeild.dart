import 'package:flutter/material.dart';
import 'package:frontend/constants/colors.dart' as appColors;

class GeneratorTextfeild extends StatelessWidget {
  const GeneratorTextfeild({super.key});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      child: Container(
        padding: EdgeInsets.symmetric(horizontal: 12),
        decoration: BoxDecoration(
          color: appColors.white.withOpacity(0.05),
          borderRadius: BorderRadius.all(Radius.circular(10))
        ),
        child: TextField(
          style: TextStyle(
            color: appColors.white,
            fontFamily: 'NSansB'
          ),
          decoration: InputDecoration(
          border: InputBorder.none,
          hintText: "Type a topic like 'Law in India'",
          hintStyle: TextStyle(
            color: appColors.white.withOpacity(0.1),
            fontFamily: 'NSansL'
          )
          ),
        ),
      ),
    );
  }
}