import 'dart:math' as math;

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:frontend/models/core_level_model.dart';
import 'package:frontend/models/full_level_content_model.dart';
import 'package:frontend/models/quiz_item_model.dart';
import 'package:frontend/pages/components/quiz_screen.dart';
import 'package:frontend/pages/quiz.dart';
import 'package:frontend/providers/quiz_page_provider.dart';
import 'package:frontend/services/services.dart';
import 'package:frontend/widgets/levels_page/level_widget.dart';
import 'package:frontend/widgets/quiz/info_dialog.dart';
import 'package:frontend/widgets/quiz/quiz_options.dart';
import 'package:frontend/widgets/quiz/quiz_question.dart';
import 'package:frontend/constants/colors.dart' as appColors;
import 'package:frontend/widgets/quiz/question_submit_button.dart';
import 'package:frontend/widgets/quiz/results_page_button.dart';
import 'package:provider/provider.dart';

class ResultScreen extends StatelessWidget {
  final LevelContentModel data;
  final MiniLevelModel shortData;
  const ResultScreen({super.key, required this.data, required this.shortData});

  @override
  Widget build(BuildContext context) {
    return Consumer<QuizPageProvider>(
      builder: (context, provider, child) => 
      Padding(
        padding: const EdgeInsets.fromLTRB(12, 12, 12, 8),
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                '🎉 That\'s Awesome',
                style: TextStyle(
                  fontFamily: 'NSansB',
                  color: appColors.white.withOpacity(1),
                  fontSize: 22
                ),
              ),
              SizedBox(height: 5,),
              Text(
                'You’ve stirred the pot—just a few more steps to your perfect Noodl!',
                style: TextStyle(
                  fontFamily: 'NSansL',
                  color: appColors.white.withOpacity(0.75),
                  fontSize: 14
                ),
              ),
              SizedBox(height: 12,),
              Stack(
                alignment: Alignment.topRight,
                children: [
                  LevelWidget(
                    nullOnTap: true,
                    data: MiniLevelModel(
                      createdAt: 'NA',
                      id: -1,
                      levelNumber: shortData.levelNumber,
                      levelTitle: data.levelTitle,
                      pathId: -1
                    ),
                  ),
                  Transform.rotate(
                    angle: math.pi/6,
                    child: Text(
                      '👑',
                      style: TextStyle(
                        fontSize: 40,
                        height: -0.4,
                        letterSpacing: -2
                      ),
                      ),
                  )
                ],
              ),
              SizedBox(height: 0,),
              Text(
                'You may now choose from one of the actions.',
                style: TextStyle(
                  fontFamily: 'NSansL',
                  color: appColors.white.withOpacity(0.75),
                  fontSize: 14
                ),
              ),
      
              // all of these should clear everything
              SizedBox(height: 12,),
              FutureBuilder(
                future: APIservice.fetchLevelsFromNoodl(pathID: shortData.pathId),
                builder: (context, snapshot) =>
                snapshot.hasData?
                  ResultsPageButton(
                    text: 'Lesson ${shortData.levelNumber+1}',
                    onTap: (){
                      provider.zeroScore();
                      provider.setNoSelectedOption();
                      provider.setProgressBarZero();

                      Navigator.of(context)
                        // ..pop()
                          .pushReplacement(
                            MaterialPageRoute(
                              builder: (context) => 
                                QuizPage(
                                  shortData: (snapshot.data!.levels)[shortData.levelNumber+1-1],
                                ),
                            )
                          );
                    }
                  ):CupertinoActivityIndicator()
              ),
      
      
      
              SizedBox(height: 12,),
              ResultsPageButton(text: 'All Lessons'),
              SizedBox(height: 12,),
              ResultsPageButton(text: 'Back Home'),
            ],
          ),
        ),
      ),
    );
  }
}