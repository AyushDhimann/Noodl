import 'dart:ffi';

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:frontend/constants/colors.dart' as appColors;
import 'package:frontend/models/noodl_model.dart';
import 'package:frontend/providers/generate_page_provider.dart';
import 'package:frontend/providers/metamask_provider.dart';
import 'package:frontend/services/services.dart';
import 'package:frontend/widgets/generate/generate_button.dart';
import 'package:frontend/widgets/generate/generator_textfeild.dart';
import 'package:frontend/widgets/home/noodl_button.dart';
import 'package:provider/provider.dart';

class NoodleGeneratorWidget extends StatefulWidget {
  const NoodleGeneratorWidget({super.key});

  @override
  State<NoodleGeneratorWidget> createState() => _NoodleGeneratorWidgetState();
}

class _NoodleGeneratorWidgetState extends State<NoodleGeneratorWidget> {

  @override
  Widget build(BuildContext context) {
    EdgeInsets dp = MediaQuery.of(context).padding;
    return Consumer2<GeneratePageProvider, MetaMaskProvider>(
      builder: (context, generatePageprovider, metaMaskProvider, child) => 
      Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: double.infinity,
            padding: EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: appColors.white.withOpacity(0.08),
              borderRadius: BorderRadius.all(Radius.circular(12.5)),
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.start,
                  children: [
                    Icon(
                      CupertinoIcons.timelapse,
                      color: appColors.white,
                    ),
                    SizedBox(width: 10),
                    Text(
                      'Noodl Generator',
                      style: TextStyle(
                        fontFamily: 'NSansB',
                        fontSize: 20,
                        color: appColors.white,
                      ),
                    ),
                  ],
                ),
                SizedBox(height: 5),
                Text(
                  'Enter a topic or skill you wish to learn—for example, ‘Introduction to Web3’ or ‘Machine Learning with Python’. Please avoid inappropriate content to ensure a meaningful learning experience.\nNot sure what to search? Tap "I’m Feeling Lucky" and we’ll pick a topic for you!',
                  style: TextStyle(
                    fontFamily: 'NSansL',
                    color: appColors.white.withOpacity(0.8),
                    fontSize: 14,
                  ),
                ),
                SizedBox(height: 12),
                Stack(
                  alignment: Alignment.center,
                  children: [
                    GeneratorTextfeild(
                      textEditingController: generatePageprovider.generatorTextEditingController,
                    ),
                    generatePageprovider.isRandomTopicLoading
                        ? Container(
                            padding: EdgeInsets.all(5),
                            decoration: BoxDecoration(
                              color: appColors.grey,
                              borderRadius: BorderRadius.all(Radius.circular(100)),
                            ),
                            child: CupertinoActivityIndicator(
                              color: appColors.white,
                            ),
                          )
                        : SizedBox.shrink(),
                  ],
                ),
                SizedBox(height: 12),
                SingleChildScrollView(
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.end,
                    children: [
                      GenerateButton(
                        altStyling: true,
                        text: 'I\'m feeling lucky',
                        onTap: () async {
                          generatePageprovider.setRandomTopicLoadingTrue();
                          String? topic = await APIservice.fetchRandomTopic();
                          generatePageprovider.setATopicInGenerationFeild(topic!);
                          generatePageprovider.setRandomTopicLoadingFalse();
                        },
                      ),
                      SizedBox(width: 8),
                      GenerateButton(
                        onTap: () async {
                          FocusScope.of(context).unfocus();
                          generatePageprovider.initialLoadingTrue();
                          generatePageprovider.similarExistsFalse();
                          final response = await APIservice.generateNoodle(
                            prompt: generatePageprovider.generatorTextEditingController.text,
                            walletAdd: metaMaskProvider.walletAddress!,
                          );

                          generatePageprovider.initialLoadingFalse();

                          if (response['message'] != 'E') {
                            if (response['error'] != null && response['similar_path'] != null) {
                              final similar = response['similar_path'];
                              generatePageprovider.setSimilarNoodl(NoodlModel(
                                  id: similar['id'],
                                  title: similar['title'],
                                  description: similar['short_description'],
                                  totalLevels: -1,
                                  createdAt: 'NA',
                                ));
                              generatePageprovider.similarExistsTrue();
                            } else {
                              generatePageprovider.setGeneratingTaskID(response['task_id']);
                            }
                          }
                        },
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          if (generatePageprovider.similarExists && generatePageprovider.similarNoodl != null)
            Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                SizedBox(height: 12),
                Text(
                  "A similar Noodl already exists!",
                  style: TextStyle(
                    fontFamily: 'NSansL',
                    fontSize: 14,
                    color: appColors.white
                  ),
                ),
                SizedBox(height: 8),
                NoodlButton(data: generatePageprovider.similarNoodl!),
                Text(
                  "If this isn’t quite what you were looking for, try refining your topic or being more specific to generate a personalized learning path.",
                  style: TextStyle(
                    fontFamily: 'NSansL',
                    fontSize: 14,
                    color: appColors.white
                  ),
                ),
                SizedBox(height: dp.bottom + 12),
              ],
            ),
        ],
      ),
    );
  }
}
