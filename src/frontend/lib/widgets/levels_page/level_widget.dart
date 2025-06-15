import 'dart:math';

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:frontend/constants/colors.dart' as appColors;
import 'package:frontend/models/core_level_model.dart';
import 'package:frontend/pages/quiz.dart';
import 'package:frontend/providers/metamask_provider.dart';
import 'package:frontend/services/services.dart';
import 'package:provider/provider.dart';

class LevelWidget extends StatefulWidget {
  final MiniLevelModel data;
  final bool nullOnTap;
  final bool alwaysFullOpacity;
  const LevelWidget({
    super.key,
    required this.data,
    this.nullOnTap = false,
    this.alwaysFullOpacity = false,
  });

  @override
  State<LevelWidget> createState() => _LevelWidgetState();
}

class _LevelWidgetState extends State<LevelWidget> {
  bool isPreviousLevelComplete = false;
  bool isCurrentLevelComplete = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      final metaMaskProvider = Provider.of<MetaMaskProvider>(
        context,
        listen: false,
      );

      final wallet = metaMaskProvider.walletAddress!;
      final pathId = widget.data.pathId;
      final currentLevel = widget.data.levelNumber;

      try {
        bool currentComplete = await APIservice.isLevelComplete(
          walletAdd: wallet,
          pathID: pathId,
          levelIndex: currentLevel,
        );

        bool prevComplete = currentLevel == 1
            ? true
            : await APIservice.isLevelComplete(
                walletAdd: wallet,
                pathID: pathId,
                levelIndex: currentLevel - 1,
              );

        if (!mounted) return;

        setState(() {
          isCurrentLevelComplete = currentComplete;
          isPreviousLevelComplete = prevComplete;
        });
      } catch (e) {
        // Optional: handle API error
        if (mounted) {
          setState(() {
            isCurrentLevelComplete = false;
            isPreviousLevelComplete = false;
          });
        }
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(bottom: 12),
      child: AnimatedOpacity(
        opacity: widget.alwaysFullOpacity
            ? 1
            : (isPreviousLevelComplete ? 1 : 0.25),
        duration: Duration(milliseconds: 200),
        child: IgnorePointer(
          ignoring: !isPreviousLevelComplete || isCurrentLevelComplete,
          child: Material(
            borderRadius: BorderRadius.all(Radius.circular(12.5)),
            color: Colors.white.withOpacity(0.08),
            child: InkWell(
              borderRadius: BorderRadius.all(Radius.circular(12.5)),
              onTap: widget.nullOnTap
                  ? null
                  : () {
                      Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (context) =>
                              QuizPage(shortData: widget.data),
                        ),
                      );
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
                          'CHAPTER',
                          style: TextStyle(
                            color: appColors.white.withOpacity(0.025),
                            fontFamily: 'NSansB',
                            letterSpacing: -1,
                            height: 1,
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
                            Container(
                              padding: EdgeInsets.symmetric(
                                vertical: 5,
                                horizontal: 8,
                              ),
                              decoration: BoxDecoration(
                                borderRadius: BorderRadius.all(
                                  Radius.circular(8),
                                ),
                                color: appColors.primary.withOpacity(0.25),
                              ),
                              child: Text(
                                'Chapter ${widget.data.levelNumber}',
                                style: TextStyle(
                                  color: appColors.white,
                                  fontSize: 16,
                                  fontFamily: 'NSansM',
                                ),
                              ),
                            ),
                            SizedBox(height: 8),
                            Row(
                              crossAxisAlignment: CrossAxisAlignment.center,
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Expanded(
                                  child: Text(
                                    widget.data.levelTitle,
                                    style: TextStyle(
                                      color: appColors.white,
                                      fontSize: 18,
                                      fontFamily: 'NSansB',
                                    ),
                                  ),
                                ),
                                Row(
                                  children: [
                                    if (isCurrentLevelComplete)
                                      Icon(
                                        CupertinoIcons.check_mark_circled_solid,
                                        color: Colors.greenAccent,
                                      ),
                                    if (!isCurrentLevelComplete)
                                      Padding(
                                        padding: const EdgeInsets.only(left: 5),
                                        child: Icon(
                                          CupertinoIcons.arrow_right,
                                          color: appColors.white,
                                        ),
                                      ),
                                  ],
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
