import 'package:flutter/material.dart';
import 'package:frontend/constants/colors.dart' as appColors;
import 'package:frontend/providers/quiz_page_provider.dart';
import 'package:frontend/widgets/quiz/question_submit_button.dart';
import 'package:provider/provider.dart';

void showQuitDialog(BuildContext context){
  Size size = MediaQuery.of(context).size;
  EdgeInsets dp = MediaQuery.of(context).padding;
  showGeneralDialog(
    context: context,
    barrierColor: appColors.black.withOpacity(0.9),
    pageBuilder: (context, animation, secondaryAnimation) {
      // KINDLY REMOVE THIS BITCCCHHH
      return Scaffold(
        backgroundColor: Colors.transparent,
        body: Center(
          child: Container(
            width: size.width - 24,
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              borderRadius: const BorderRadius.all(Radius.circular(18)),
              color: appColors.grey
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                Text(
                  'Quit',
                  // 'You\'re Wrong!',
                  style: TextStyle(
                    fontFamily: 'NSansB',
                    color: appColors.white,
                    fontSize: 22
                  ),
                ),
                const SizedBox(height: 5,),
                Text(
                  "Are You Sure?",
                  style: TextStyle(
                    color: appColors.white,
                    fontFamily: 'NSansM',
                    fontSize: 18
                  ),
                ),
                const SizedBox(height: 5,),
                Text(
                  "You will lose progress on quitting in between a lesson.",
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: appColors.white.withOpacity(0.75),
                    fontFamily: 'NSansL',
                    fontSize: 16
                  ),
                ),
                const SizedBox(height: 20,),
                Consumer<QuizPageProvider>(
                  builder: (context, provider, child) => 
                  Row(
                    children: [
                      QuitDialogButton(
                        text: 'Quit',
                        onTap: (){
                          Provider.of<QuizPageProvider>(context, listen: false).setProgressBarZero();
                          Provider.of<QuizPageProvider>(context, listen: false).setNoSelectedOption();
                          Navigator.of(context)..pop()..pop();
                        },
                      ),
                      SizedBox(width: 8,),
                      QuitDialogButton(
                        text: 'Cancel',
                        altStyling: true,
                        onTap: () {
                          Navigator.of(context).pop();
                        },
                      ),
                    ],
                  ),
                )
              ],  
            ),
          ),
        ),
      );
    },
  );
}


class QuitDialogButton extends StatelessWidget {
  final VoidCallback? onTap;
  final String text;
  final bool altStyling;
  const QuitDialogButton({super.key, this.onTap, required this.text, this.altStyling=false});

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Material(
        color: altStyling?appColors.transparent:appColors.primary,
        borderRadius: const BorderRadius.all(Radius.circular(100)),
        child: InkWell(
          onTap: onTap,
          borderRadius: const BorderRadius.all(Radius.circular(100)),
          child: Container(
            padding: const EdgeInsets.all(12),
            alignment: Alignment.center,
            decoration: altStyling?BoxDecoration(
              border: Border.all(width: 1, color: appColors.white.withOpacity(0.75)),
              borderRadius: const BorderRadius.all(Radius.circular(100)),
            ):null,
            child: Text(
              text,
              style: TextStyle(
                color: altStyling?appColors.white: appColors.bgColor,
                fontFamily: 'NSansM',
                fontSize: 18
              ),
            ),
          ),
        ),
      ),
    );
  }
}