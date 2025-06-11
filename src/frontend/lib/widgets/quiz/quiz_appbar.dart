import 'dart:ui';

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:frontend/providers/quiz_page_provider.dart';
import 'package:frontend/widgets/quiz/quit_dialog.dart';
// import 'package:frontend/widgets/quiz/quiz_appbar_button.dart';
import 'package:marquee/marquee.dart';
import 'package:frontend/constants/colors.dart' as appColors;
import 'package:provider/provider.dart';

class QuizAppBar extends StatelessWidget {
  final String title;
  const QuizAppBar({super.key, required this.title});

  @override
  Widget build(BuildContext context) {
    Size size = MediaQuery.of(context).size;
    EdgeInsets dp = MediaQuery.of(context).padding;
    return Container(
      padding: EdgeInsets.fromLTRB(8, dp.top+8, 8, 16),
      height: dp.top + 58.25,
      // ignore: prefer_const_constructors
      child: Stack(
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              // Opacity(opacity: 1,child: QuizAppbarButton()),
              SizedBox(width: 12,),
              Expanded(
                child: Marquee(
                  text: title,
                  // pauseAfterRound: Duration(seconds: 5),
                  startAfter: Duration(seconds: 5),
                  pauseAfterRound: Duration(seconds: 5),
                  decelerationCurve: Curves.easeIn,
                  // blankSpace: size.width-24-50-8-60 , // assuming text is atleat 30 lol
                  blankSpace: size.width-24-60 , // assuming text is atleat 30 lol
                  // blankSpace: size.width/2,
                  style: TextStyle(
                    fontFamily: 'NSansB',
                    fontSize: 18,
                    // overflow: TextOverflow.ellipsis
                  ),
                ),
              ),
              // SizedBox(width: 20,),
              SizedBox(width: 12,),
              // Opacity(opacity: 0,child: QuizAppbarButton()),
              // QuizAppbarButton(),
          
            ],
          ),
          Align(
            alignment: Alignment.centerRight,
            child: ClipRRect(
              borderRadius: BorderRadius.all(Radius.circular(100)),
              child: BackdropFilter(
                filter: ImageFilter.blur(sigmaX: 30, sigmaY: 30),
                child: Material(
                  borderRadius: BorderRadius.all(Radius.circular(100)),
                  color: appColors.white.withOpacity(0.1),
                  // color: appColors.red.withOpacity(0.85),
                  child: InkWell(
                    borderRadius: BorderRadius.all(Radius.circular(100)),
                    splashColor: appColors.white.withOpacity(0.5),
                    onTap: () {
                      // Provider.of<QuizPageProvider>(context, listen: false).setProgressBarZero();
                      // Provider.of<QuizPageProvider>(context, listen: false).setNoSelectedOption();
                      // Navigator.of(context)..pop()..pop();
                      // pops twice, wohooooo
                      showQuitDialog(context);
                      },
                    child: Container(
                      padding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text(
                            'Quit',
                            style: TextStyle(
                              fontFamily: 'NSansM',
                              fontSize: 16, 
                              color: appColors.red
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
        
        ],
      ),
    );
  }
}

