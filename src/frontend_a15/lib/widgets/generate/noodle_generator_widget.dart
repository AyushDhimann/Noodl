import 'dart:ffi';

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:frontend/constants/colors.dart' as appColors;
import 'package:frontend/providers/generate_page_provider.dart';
import 'package:frontend/providers/metamask_provider.dart';
import 'package:frontend/services/services.dart';
import 'package:frontend/widgets/generate/generate_button.dart';
import 'package:frontend/widgets/generate/generator_textfeild.dart';
import 'package:provider/provider.dart';

class NoodleGeneratorWidget extends StatelessWidget {
  const NoodleGeneratorWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer2<GeneratePageProvider, MetaMaskProvider>(
      builder: (context, generatePageprovider, metaMaskProvider, child) => 
      Container(
        width: double.infinity,
        padding: EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: appColors.white.withOpacity(0.08),
          borderRadius: BorderRadius.all(Radius.circular(12.5))
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
                SizedBox(width: 10,),
                Text(
                  'Noodl Generator',
                  style: TextStyle(
                    fontFamily: 'NSansB',
                    fontSize: 20, 
                    color: appColors.white
                  ),
                ),
              ],
            ),
            SizedBox(height: 5,),
            Text(
              'Enter a topic or skill you wish to learn—for example, ‘Introduction to Web3’ or ‘Machine Learning with Python’. Please avoid inappropriate content to ensure a meaningful learning experience.\nNot sure what to search? Tap "I’m Feeling Lucky" and we’ll pick a topic for you!',
              style: TextStyle(
                fontFamily: 'NSansL',
                color: appColors.white.withOpacity(0.8),
                fontSize: 14
              ),
            ),
            SizedBox(height: 12,),
            Stack(
              alignment: Alignment.center,
              children: [
                GeneratorTextfeild(textEditingController: generatePageprovider.generatorTextEditingController,),
                generatePageprovider.isRandomTopicLoading?
                Container(
                  padding: EdgeInsets.all(5),
                  decoration: BoxDecoration(
                    color: appColors.grey,
                    borderRadius: BorderRadius.all(Radius.circular(100))
                  ),
                  child: CupertinoActivityIndicator(
                    color: appColors.white,
                  )):SizedBox.shrink(),
              ],
            ),
            SizedBox(height: 12,),
            SingleChildScrollView(
              child: Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  GenerateButton(
                    altStyling: true,
                    text: 'I\'m feeling lucky',
                    onTap: () async{
                      generatePageprovider.setRandomTopicLoadingTrue();
                      String? topic = await APIservice.fetchRandomTopic();
                      generatePageprovider.setATopicInGenerationFeild(topic!);
                      generatePageprovider.setRandomTopicLoadingFalse();
                    },
                  ),
                  SizedBox(width: 8,),
                  GenerateButton(
                    onTap: () async{
                      FocusScope.of(context).unfocus();
                      generatePageprovider.initialLoadingTrue();
                      dynamic response = await APIservice.generateNoodle(
                        prompt: generatePageprovider.generatorTextEditingController.text,
                        walletAdd: metaMaskProvider.walletAddress!
                        // ??"0x718fafb76e1631f5945bf58104f3b81d9588819b",
                        // user_wallet_id: "0x718fafb76e1631f5945bf58104f3b81d9588819b"
                      );
                      generatePageprovider.initialLoadingFalse();
                      response['message'] != 'E'?
                        generatePageprovider.setGeneratingTaskID(response['task_id'])
                          :null;
                      print(generatePageprovider.generatingTaskID);
                      
                    },
                    // onTap: () {
                    //   print(metaMaskProvider.walletAddress!);
                    //   print(generatePageprovider.generatorTextEditingController.text);
                    // },
                  ),
                ],
              ),
            )
          ],
        ),
      ),
    );
  }
}