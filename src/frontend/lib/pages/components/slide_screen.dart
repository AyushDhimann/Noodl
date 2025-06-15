import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:frontend/constants/colors.dart' as appColors;
import 'package:frontend/constants/helper_functions.dart';
import 'package:frontend/models/slide_item_model.dart';
import 'package:frontend/providers/quiz_page_provider.dart';
import 'package:frontend/services/ms_tts.dart' as msTTS;
// import 'package:markdown_widget/markdown_widget.dart';
import 'package:provider/provider.dart';

class SlideScreen extends StatelessWidget {
  final SlideItemModel data;
  const SlideScreen({super.key, required this.data});

  @override
  Widget build(BuildContext context) {
    final audioPlayer = AudioPlayer();

    Size size = MediaQuery.of(context).size;
    EdgeInsets dp = MediaQuery.of(context).padding;
    return Padding(
      padding: EdgeInsetsGeometry.fromLTRB(12, 12, 12, dp.bottom + 12),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Text(
          //   '💡 Did You Know?',
          //   style: TextStyle(
          //     color: appColors.white,
          //     fontSize: 20,
          //     fontFamily: 'NSansB'
          //   ),
          // ),
          // SizedBox(height: 5,),
          // Text(
          //   'India was the first country to nationalize its banks in 1969, bringing 14 major private banks under government control to ensure financial inclusion and rural development.',
          //   style: TextStyle(
          //     color: appColors.white,
          //     fontSize: 18,
          //     fontFamily: 'NSansm'
          //   ),
          // ),
          // const SizedBox(height: 5,),
          // Text(
          //   '📈 This move drastically increased the number of bank branches in rural areas and played a major role in improving access to credit across the country.',
          //   style: TextStyle(
          //     color: appColors.white,
          //     fontSize: 18,
          //     fontFamily: 'NSansL'
          //   ),
          // ),
          Expanded(
            child: Markdown(
              data: data.content,
              padding: EdgeInsets.zero,
              styleSheet: MarkdownStyleSheet(
                h2: TextStyle(
                  fontFamily: 'NSansB',
                  fontSize: 22,
                  color: appColors.white,
                ),
                h1: TextStyle(
                  fontFamily: 'NSansB',
                  fontSize: 22,
                  color: appColors.white,
                ),
                h3: TextStyle(
                  fontFamily: 'NSansB',
                  fontSize: 22,
                  color: appColors.white,
                ),
                p: TextStyle(
                  fontFamily: 'NSansL',
                  fontSize: 16,
                  color: appColors.white,
                  backgroundColor: appColors.black,
                ),
                strong: TextStyle(
                  fontFamily: 'NSansB',
                  fontSize: 16,
                  color: appColors.white,
                ),
                code: TextStyle(fontFamily: 'MonolisaRI', fontSize: 16),
              ),
            ),
          ),
          // Text(data.content),
          const SizedBox(height: 10),
          Consumer<QuizPageProvider>(
            builder: (context, provider, child) => SizedBox(
              width: size.width,
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  SizedBox(width: 50),
                  Material(
                    borderRadius: const BorderRadius.all(Radius.circular(25)),
                    color: appColors.white,
                    child: InkWell(
                      onTap: () async{
                        provider.goToNextQues();
                        await msTTS.stopTtsAudio();
                        provider.ttsCompleteFalse();
                        provider.ttsLoadingFalse();
                        provider.ttsPlayingFalse();
                      },
                      splashColor: Colors.black12,
                      borderRadius: const BorderRadius.all(Radius.circular(25)),
                      child: Container(
                        width: size.width / 2,
                        height: 50,
                        alignment: Alignment.center,
                        child: Icon(
                          CupertinoIcons.arrow_right,
                          color: appColors.black,
                        ),
                      ),
                    ),
                  ),
                  provider.ttsLoading?Container(
                    width: 50,
                    height: 50,
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.all(Radius.circular(100)),
                      color: appColors.white
                    ),
                    alignment: Alignment.center,
                    child: CupertinoActivityIndicator(
                      color: appColors.black,
                    ),
                  ):
                  Material(
                    borderRadius: const BorderRadius.all(Radius.circular(25)),
                    color: appColors.white,
                    child: InkWell(
                      onTap: () async {
                        if (!provider.ttsPlaying) {
                          provider.ttsCompleteFalse();
                          provider.ttsLoadingTrue();
                          await msTTS.playTtsFromFile(
                            HelperFunctions.markdownToPlainText(data.content),
                            context
                          );
                          provider.ttsLoadingFalse();
                          provider.ttsPlayingTrue();
                        } else {
                          await msTTS.stopTtsAudio();
                          provider.ttsPlayingFalse();
                          provider.ttsCompleteFalse();
                        }
                      },
                      splashColor: Colors.black12,
                      borderRadius: const BorderRadius.all(Radius.circular(25)),
                      child: Container(
                        width: 50,
                        height: 50,
                        alignment: Alignment.center,
                        child: Icon(
                          provider.ttsPlaying && !provider.ttsComplete?
                          CupertinoIcons.speaker_slash:
                          CupertinoIcons.speaker_2,
                          color: appColors.black,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
