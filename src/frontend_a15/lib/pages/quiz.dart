import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:frontend/models/core_level_model.dart';
import 'package:frontend/models/full_level_content_model.dart';
import 'package:frontend/models/quiz_item_model.dart';
import 'package:frontend/pages/components/result_screen.dart';
import 'package:frontend/pages/components/slide_screen.dart';
import 'package:frontend/pages/components/quiz_screen.dart';
import 'package:frontend/providers/quiz_page_provider.dart';
import 'package:frontend/services/services.dart';
import 'package:frontend/widgets/quiz/quiz_appbar.dart';
import 'package:frontend/constants/colors.dart' as appColors;
import 'package:provider/provider.dart';
class QuizPage extends StatefulWidget {
  final MiniLevelModel shortData;
  const QuizPage({super.key, required this.shortData});

  @override
  State<QuizPage> createState() => _QuizPageState();
}

class _QuizPageState extends State<QuizPage> {
  late Future<LevelContentModel?> _futureLevelData;

  @override
  void initState() {
    super.initState();
    _futureLevelData = APIservice.fetchLevelContent(
      pathID: widget.shortData.pathId,
      levelID: widget.shortData.levelNumber,
    );
  }

  @override
  Widget build(BuildContext context) {
    Size size = MediaQuery.of(context).size;
    EdgeInsets dp = MediaQuery.of(context).padding;

    return PopScope(
      canPop: false,
      child: Scaffold(
        backgroundColor: appColors.bgColor,
        body: Consumer<QuizPageProvider>(
          builder: (context, provider, child) => 
          Stack(
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  QuizAppBar(
                    title: widget.shortData.levelTitle,
                    showQuit: provider.totalItemsInLesson > provider.progress,
                  ),
                  SizedBox(
                    width: size.width,
                    height: size.height - dp.top - 58.25,
                    child: FutureBuilder<LevelContentModel?>(
                      future: _futureLevelData,
                      builder: (context, snapshot) {
                        if (snapshot.connectionState == ConnectionState.done && snapshot.hasData) {
                          final totalItemsInLevel = snapshot.data!.totalQuestionsInLevel + snapshot.data!.totalSlidesInLevel;

                          // Only call once
                          if (provider.totalItemsInLesson == 0) {
                            WidgetsBinding.instance.addPostFrameCallback((_) {
                              provider.setTotalQuestions(totalItemsInLevel);
                            });
                          }

                          return Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              SizedBox(
                                height: 2,
                                child: LinearProgressIndicator(
                                  value: provider.progress / totalItemsInLevel,
                                  color: appColors.accent,
                                ),
                              ),
                              SizedBox(
                                width: size.width,
                                height: size.height - dp.top - 58.25 - 2,
                                child: PageView(
                                  controller: provider.quizQuesContoller,
                                  physics: NeverScrollableScrollPhysics(),
                                  children: [
                                    ...snapshot.data!.items.map((e) {
                                      if (e is QuizItemModel) {
                                        return QuizScreen(data: e);
                                      }
                                      return SlideScreen(data: e);
                                    }),
                                    ResultScreen(data: snapshot.data!, shortData: widget.shortData),
                                  ],
                                ),
                              ),
                            ],
                          );
                        }

                        return Column(
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
                              height: size.height - dp.top - 58.25 - 2,
                              child: const Center(child: CupertinoActivityIndicator()),
                            ),
                          ],
                        );
                      },
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
