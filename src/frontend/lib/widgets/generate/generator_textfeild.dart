import 'package:flutter/material.dart';
import 'package:frontend/constants/colors.dart' as appColors;

class GeneratorTextfeild extends StatelessWidget {
  final TextEditingController? textEditingController;
  final String? hintText;
  final double? opacity;
  final double? hintOpacity;
  const GeneratorTextfeild({super.key, this.textEditingController, this.hintText, this.opacity, this.hintOpacity});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      child: Container(
        padding: EdgeInsets.symmetric(horizontal: 12),
        decoration: BoxDecoration(
          color: appColors.white.withOpacity(opacity??0.05),
          borderRadius: BorderRadius.all(Radius.circular(10))
        ),
        child: TextField(
          controller: textEditingController,
          style: TextStyle(
            color: appColors.white,
            fontFamily: 'NSansB'
          ),
          decoration: InputDecoration(
          border: InputBorder.none,
          hintText: hintText??"Type a topic like 'Law in India'",
          hintStyle: TextStyle(
            color: appColors.white.withOpacity(hintOpacity??0.1),
            fontFamily: 'NSansL'
          )
          ),
        ),
      ),
    );
  }
}