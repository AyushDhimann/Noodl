import 'package:flutter/material.dart';
import 'package:frontend/constants/colors.dart' as appColors;
import 'package:frontend/providers/quiz_page_provider.dart';
import 'package:frontend/widgets/quiz/quiz_submit_button.dart';
import 'package:provider/provider.dart';

void showInfoDialog(BuildContext context){
  Size size = MediaQuery.of(context).size;
  EdgeInsets dp = MediaQuery.of(context).padding;
  showGeneralDialog(
    context: context,
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
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(12),
                  alignment: Alignment.center,
                  decoration: BoxDecoration(
                    color: appColors.primary.withOpacity(0.25),
                    // color: appColors.red.withOpacity(0.75),
                    borderRadius: const BorderRadius.all(Radius.circular(12.5))
                  ),
                  child: Text(
                    'You\'re Correct!',
                    // 'You\'re Wrong!',
                    style: TextStyle(
                      fontFamily: 'NSansM',
                      color: appColors.white,
                      fontSize: 20
                    ),
                  ),
                ),
                const SizedBox(height: 18,),
                Text(
                  "💡 Explanation:\nThe Reserve Bank of India (RBI) is the central bank of the country. It is responsible for issuing and regulating the Indian currency (₹), controlling inflation, managing monetary policy, and ensuring financial stability. It does not give loans to individuals or collect taxes—that’s handled by commercial banks and the Income Tax Department, respectively.",
                  style: TextStyle(
                    color: appColors.white,
                    fontFamily: 'NSansM',
                    fontSize: 18
                  ),
                ),
                const SizedBox(height: 20,),
                Consumer<QuizPageProvider>(
                  builder: (context, provider, child) => 
                  Material(
                    color: appColors.white,
                    borderRadius: const BorderRadius.all(Radius.circular(12.5)),
                    child: InkWell(
                      onTap: (){
                        provider.goToNextQues();
                        Navigator.of(context).pop();
                      },
                      borderRadius: const BorderRadius.all(Radius.circular(12.5)),
                      child: Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(12),
                        alignment: Alignment.center,
                        child: Text(
                          'Continue',
                          style: TextStyle(
                            color: appColors.bgColor,
                            fontFamily: 'NSansM',
                            fontSize: 18
                          ),
                        ),
                      ),
                    ),
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