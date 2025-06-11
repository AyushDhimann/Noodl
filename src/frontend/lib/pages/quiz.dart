import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:frontend/models/core_level_model.dart';
import 'package:frontend/models/full_level_content_model.dart';
import 'package:frontend/models/quiz_item_model.dart';
import 'package:frontend/pages/components/slide_screen.dart';
import 'package:frontend/pages/components/quiz_screen.dart';
import 'package:frontend/providers/quiz_page_provider.dart';
import 'package:frontend/services/services.dart';
import 'package:frontend/widgets/quiz/info_dialog.dart';
import 'package:frontend/widgets/quiz/quiz_appbar.dart';
// ignore: library_prefixes
import 'package:frontend/constants/colors.dart' as appColors;
// import 'package:frontend/widgets/quiz/quiz_options.dart';
// import 'package:frontend/widgets/quiz/quiz_question.dart';
import 'package:frontend/widgets/quiz/question_submit_button.dart';
import 'package:provider/provider.dart';

class QuizPage extends StatelessWidget {
  // final LevelContentModel data;
  final MiniLevelModel shortData;
  const QuizPage({super.key, required this.shortData});

  @override
  Widget build(BuildContext context) {
    // ignore: unused_local_variable
    Size size = MediaQuery.of(context).size;
    EdgeInsets dp = MediaQuery.of(context).padding;
    // ignore: prefer_const_constructors
    return PopScope(
      canPop: false,
      child: Scaffold(
        backgroundColor: appColors.bgColor,
        body:  Consumer<QuizPageProvider>(
          builder: (context, provider, child) => 
          Stack(
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  QuizAppBar(title: '${shortData.levelTitle}',),
                  SizedBox(
                    width: size.width,
                    height: size.height - dp.top -58.25,
                    child: FutureBuilder(
                      future: APIservice.fetchLevelContent(pathID: shortData.pathId, levelID: shortData.levelNumber),
                      builder: (context, snapshot) =>
                      snapshot.hasData?
                      Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          SizedBox(
                            height: 2,
                            child: LinearProgressIndicator(
                              value: provider.progress/(snapshot.data!.totalQuestionsInLevel+snapshot.data!.totalSlidesInLevel),
                              color: appColors.accent,
                            ),
                          ),
                          SizedBox(
                            width: size.width,
                            height: size.height - dp.top -58.25 -2,
                            child: PageView(
                              controller: provider.quizQuesContoller,
                              physics: NeverScrollableScrollPhysics(),
                              children: [
                                ...snapshot.data!.items.map(
                                  (e) {
                                    if(e is QuizItemModel){
                                      return QuizScreen(data: e);
                                    } 
                                    return SlideScreen(data: e);
                                  },
                                ),
                              ],
                            ),
                          ),
                        ],
                      ) : Column(
                        crossAxisAlignment: CrossAxisAlignment.center,
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Container(
                            width: size.width,
                            height: 2,
                            color: appColors.primary.withOpacity(0.5),
                          ),
                          SizedBox(
                            width: size.width,
                            height: size.height - dp.top -58.25 -2,
                            child: Center(
                              child: CupertinoActivityIndicator()
                              )
                            ),
                        ],
                      ),
                    ),
                  )
                ],
              ),
              
            ],
          ),
        ),
      ),
    );
  }
}