import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:frontend/constants/colors.dart' as appColors;
import 'package:markdown_widget/markdown_widget.dart';

class QuizQuestion extends StatelessWidget {
  final String text;
  const QuizQuestion({super.key, required this.text});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 15),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: appColors.primary.withOpacity(0.25),
        borderRadius: const BorderRadius.all(Radius.circular(12.5))
      ),
      child: Markdown(
        data: text,
        padding: EdgeInsets.zero,
        styleSheet: MarkdownStyleSheet(
          p: TextStyle(
            fontSize: 20,
            fontFamily: 'NSansM'
          )
        ),
        physics: NeverScrollableScrollPhysics(),
        shrinkWrap: true,
      ),
      // child: Text(
      //   text,
      //   style: TextStyle(
      //     color: appColors.white,
      //     fontFamily: 'NSansM',
      //     fontSize: 20
      //   ),
      // ),
    );
  }
}