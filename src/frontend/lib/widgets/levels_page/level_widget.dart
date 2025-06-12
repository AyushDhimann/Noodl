// LEVEL PAGE/ LESSON PAGE

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:frontend/constants/colors.dart' as appColors;
import 'package:frontend/models/core_level_model.dart';
import 'package:frontend/models/noodl_model.dart';
import 'package:frontend/pages/levels_page.dart';
import 'package:frontend/pages/quiz.dart';
import 'package:frontend/providers/metamask_provider.dart';
import 'package:frontend/services/services.dart';
import 'package:provider/provider.dart';

class LevelWidget extends StatelessWidget {
  final MiniLevelModel data;
  const LevelWidget({super.key, required this.data,});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(bottom: 12),
      child: Material(
        borderRadius: BorderRadius.all(Radius.circular(12.5)),
        color: Colors.white.withOpacity(0.08),
        child: InkWell(
        borderRadius: BorderRadius.all(Radius.circular(12.5)),
          onTap: () {
            // remove hardcoded wallet add
            String userWalletAdd = Provider.of<MetaMaskProvider>(context).walletAddress
              ??"0x718fafb76e1631f5945bf58104f3b81d9588819b";

            APIservice.postStartUserProgress(walletAdd: userWalletAdd, pathID: data.pathId);
            Navigator.of(context).push(MaterialPageRoute(builder: (context) => QuizPage(shortData: data,),));
          },
          child: SizedBox(
            width: double.infinity,
            child: Stack(
              alignment: Alignment.center,
              children: [
                SizedBox(
                  width: double.infinity,
                  child: FittedBox(
                    fit: BoxFit.cover,
                    child: Text(
                      'LESSON',
                      style: TextStyle(
                        color: appColors.white.withOpacity(0.025),
                        // fontFamily: 'MonolisaBB',
                        fontFamily: 'NSansB',
                        letterSpacing: -1,
                        height: 1
                      ),
                    ),
                  ),
                ),
                Align(
                  alignment: Alignment.topLeft,
                  child: Padding(
                    padding: EdgeInsets.all(12),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Text(
                        //   '#1',
                        //   style: TextStyle(
                        //     fontSize: 14,
                        //     fontFamily: 'NSansM',
                        //     color: appColors.white.withOpacity(0.5)
                        //   ),
                        // ),
                        // SizedBox(height: 5,),
                        Container(
                          padding: EdgeInsets.symmetric(vertical: 5, horizontal: 8),
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.all(Radius.circular(8)),
                            color: appColors.primary.withOpacity(0.25)
                          ),
                          child: Text(
                            'Lesson ${data.levelNumber}',
                            style: TextStyle(
                              color: appColors.white,
                              fontSize: 16,
                              fontFamily: 'NSansM'
                            ),
                          ),
                        ),
                        SizedBox(height: 8,),
                        Row(
                          crossAxisAlignment: CrossAxisAlignment.center,
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Expanded(
                              child: Text(
                                data.levelTitle,
                                style: TextStyle(
                                  color: appColors.white,
                                  fontSize: 18,
                                  fontFamily: 'NSansB'
                                ),
                              ),
                            ),
                            SizedBox(height: 5,),
                            Icon(
                              CupertinoIcons.arrow_right,
                              color: appColors.white,
                            )
                          ],
                        ),
                        
                      ],
                    ),
                  ),
                )
              ],
            ),
          ),
        ),
      ),
    );
  }
}