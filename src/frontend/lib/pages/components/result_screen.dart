import 'dart:math' as math;

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:frontend/models/core_level_model.dart';
import 'package:frontend/models/full_level_content_model.dart';
import 'package:frontend/models/quiz_item_model.dart';
import 'package:frontend/pages/components/quiz_screen.dart';
import 'package:frontend/pages/home.dart';
import 'package:frontend/pages/levels_page.dart';
import 'package:frontend/pages/nft_page.dart';
import 'package:frontend/pages/quiz.dart';
import 'package:frontend/providers/metamask_provider.dart';
import 'package:frontend/providers/quiz_page_provider.dart';
import 'package:frontend/services/services.dart';
import 'package:frontend/widgets/generate/starting_generation.dart';
import 'package:frontend/widgets/levels_page/level_widget.dart';
import 'package:frontend/widgets/quiz/info_dialog.dart';
import 'package:frontend/widgets/quiz/quiz_options.dart';
import 'package:frontend/widgets/quiz/quiz_question.dart';
import 'package:frontend/constants/colors.dart' as appColors;
import 'package:frontend/widgets/quiz/question_submit_button.dart';
import 'package:frontend/widgets/quiz/results_page_button.dart';
import 'package:provider/provider.dart';

class ResultScreen extends StatefulWidget {
  final LevelContentModel data;
  final MiniLevelModel shortData;
  const ResultScreen({super.key, required this.data, required this.shortData});

  @override
  State<ResultScreen> createState() => _ResultScreenState();
}

class _ResultScreenState extends State<ResultScreen> {
  @override
  void initState() {
    super.initState();

    WidgetsBinding.instance.addPostFrameCallback((_) async {
      final quizProvider = Provider.of<QuizPageProvider>(
        context,
        listen: false,
      );
      final metaMaskProvider = Provider.of<MetaMaskProvider>(
        context,
        listen: false,
      );

      APIservice.sendUserScore(
        walletAdd: metaMaskProvider.walletAddress!,
        pathID: widget.shortData.pathId,
        levelIndex: widget.shortData.levelNumber,
        correctAnswers: quizProvider.correctAnswers,
        totalQuestions: quizProvider.questionCount,
      );

      //  bool isNoodlComplete = await APIservice.isNoodlComplete(walletAdd: metaMaskProvider.walletAddress??'0x718fafb76e1631f5945bf58104f3b81d9588819b', pathID: widget.shortData.pathId);
    });
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder(
      future: APIservice.fetchLevelsFromNoodl(pathID: widget.shortData.pathId),
      builder: (context, snapshot) {
        return snapshot.hasData
            ? Consumer<QuizPageProvider>(
                builder: (context, provider, child) {
                  // send a request to check if noodl is complete
                  bool isLastLevel =
                      widget.shortData.levelNumber ==
                      snapshot.data!.totalLevels;
                  return Padding(
                    padding: const EdgeInsets.fromLTRB(12, 12, 12, 8),
                    child: SingleChildScrollView(
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            isLastLevel
                                ? '🎓You Graduated This Noodl!'
                                : '🎉 That\'s Awesome',
                            style: TextStyle(
                              fontFamily: 'NSansB',
                              color: appColors.white.withOpacity(1),
                              fontSize: 22,
                            ),
                          ),
                          SizedBox(height: 5),
                          Text(
                            isLastLevel
                                ? 'From your first stir to final slurp, brilliance all the way through. In short, you\'ve completed all the lessons in this Noodl. Congratulations!'
                                : 'You’ve stirred the pot, just a few more steps to your perfect Noodl!',
                            style: TextStyle(
                              fontFamily: 'NSansL',
                              color: appColors.white.withOpacity(0.75),
                              fontSize: 14,
                            ),
                          ),
                          SizedBox(height: 12),
                          Stack(
                            alignment: Alignment.topRight,
                            children: [
                              LevelWidget(
                                alwaysFullOpacity: true,
                                nullOnTap: true,
                                data: MiniLevelModel(
                                  createdAt: 'NA',
                                  id: -1,
                                  levelNumber: widget.shortData.levelNumber,
                                  levelTitle: widget.data.levelTitle,
                                  pathId: -1,
                                ),
                              ),
                              Transform.rotate(
                                angle: math.pi / 6,
                                child: Text(
                                  '👑',
                                  style: TextStyle(
                                    fontSize: 40,
                                    height: -0.4,
                                    letterSpacing: -2,
                                  ),
                                ),
                              ),
                            ],
                          ),
                          Text(
                            isLastLevel
                                ? 'You’ve officially cooked the whole Noodl!'
                                : 'You may now choose from one of the actions.',
                            style: TextStyle(
                              fontFamily: 'NSansL',
                              color: appColors.white.withOpacity(0.75),
                              fontSize: 14,
                            ),
                          ),

                          isLastLevel
                              ? Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    FutureBuilder(
                                      future: APIservice.mintNFT(
                                        pathID: widget.shortData.pathId,
                                        walletAdd:
                                            Provider.of<MetaMaskProvider>(
                                              context,
                                            ).walletAddress!,
                                      ),
                                      builder: (context, snapshot) =>
                                          snapshot.hasData
                                          ? Column(
                                              mainAxisSize: MainAxisSize.min,
                                              crossAxisAlignment:
                                                  CrossAxisAlignment.start,
                                              children: [
                                                Text(
                                                  'Your NFT badge of honor is ready to be claimed.',
                                                  style: TextStyle(
                                                    fontFamily: 'NSansL',
                                                    color: appColors.white
                                                        .withOpacity(0.75),
                                                    fontSize: 14,
                                                  ),
                                                ),
                                                ResultsPageButton(
                                                  text: 'My NFTs',
                                                  onTap: () {
                                                    provider.zeroScore();
                                                    provider
                                                        .setNoSelectedOption();
                                                    provider
                                                        .setProgressBarZero();
                                                    provider.zeroScore();
                                                    provider
                                                        .zeroQuestionCount();

                                                    Navigator.of(
                                                      context,
                                                    ).pushReplacement(
                                                      MaterialPageRoute(
                                                        builder: (context) =>
                                                            NftPage(),
                                                      ),
                                                    );
                                                  },
                                                ),
                                              ],
                                            )
                                          : Padding(
                                            padding: const EdgeInsets.only(top: 12),
                                            child: LoadingStartingGenerationWidget(),
                                          ),
                                    ),
                                    ResultsPageButton(
                                      text: 'Home',
                                      onTap: () {
                                        provider.zeroScore();
                                        provider.setNoSelectedOption();
                                        provider.setProgressBarZero();
                                        provider.zeroScore();
                                        provider.zeroQuestionCount();

                                        Navigator.of(context)
                                          ..pop()
                                          ..pushReplacement(
                                            MaterialPageRoute(
                                              builder: (context) => HomePage(),
                                            ),
                                          );
                                      },
                                    ),
                                  ],
                                )
                              : Column(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    widget.shortData.levelNumber ==
                                            snapshot.data!.totalLevels
                                        ? SizedBox.shrink()
                                        : ResultsPageButton(
                                            text:
                                                'Lesson ${widget.shortData.levelNumber + 1}',
                                            onTap: () {
                                              // add api endpoint to push score
                                              provider.zeroScore();
                                              provider.setNoSelectedOption();
                                              provider.setProgressBarZero();
                                              provider.zeroQuestionCount();

                                              // provider.zeroQuestionCount();

                                              Navigator.of(
                                                context,
                                              ).pushReplacement(
                                                MaterialPageRoute(
                                                  builder: (context) => QuizPage(
                                                    shortData:
                                                        (snapshot
                                                            .data!
                                                            .levels)[widget
                                                                .shortData
                                                                .levelNumber +
                                                            1 -
                                                            1],
                                                  ),
                                                ),
                                              );
                                            },
                                          ),
                                    ResultsPageButton(
                                      text: 'All Lessons',
                                      onTap: () {
                                        provider.zeroScore();
                                        provider.setNoSelectedOption();
                                        provider.setProgressBarZero();
                                        Navigator.of(context).pop();
                                      },
                                    ),

                                    ResultsPageButton(
                                      text: 'Back Home',
                                      onTap: () {
                                        provider.zeroScore();
                                        provider.setNoSelectedOption();
                                        provider.setProgressBarZero();
                                        provider.zeroQuestionCount();
                                        Navigator.of(context)
                                          ..pop()
                                          ..pushReplacement(
                                            MaterialPageRoute(
                                              builder: (context) => HomePage(),
                                            ),
                                          );
                                      },
                                    ),
                                  ],
                                ),
                        ],
                      ),
                    ),
                  );
                },
              )
            : Center(child: CupertinoActivityIndicator());
      },
    );
  }
}
