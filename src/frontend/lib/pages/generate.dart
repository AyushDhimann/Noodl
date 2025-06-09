import 'dart:convert';

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:frontend/test/test_data.dart' as testData;
import 'package:frontend/widgets/generate/logs_display.dart';
import 'package:frontend/providers/generate_page_provider.dart';
import 'package:frontend/services/services.dart';
import 'package:frontend/widgets/common/topbar.dart';
import 'package:frontend/constants/colors.dart' as appColors;
import 'package:frontend/widgets/generate/noodle_generator_widget.dart';
import 'package:frontend/widgets/generate/starting_generation.dart';
import 'package:frontend/widgets/home/noodl_button.dart';
import 'package:provider/provider.dart';

class GenerateNoodlPage extends StatelessWidget {
  const GenerateNoodlPage({super.key});

  @override
  Widget build(BuildContext context) {
    EdgeInsets dp = MediaQuery.of(context).padding;
    Size size = MediaQuery.of(context).size;
    return GestureDetector(
      onTap: ()=>FocusScope.of(context).unfocus(),
      child: Scaffold(
        backgroundColor: appColors.bgColor,
        body: Consumer<GeneratePageProvider>(
          builder: (context, provider, child) => 
          Stack(
            children: [
              Padding(
                padding: EdgeInsetsGeometry.symmetric(horizontal: 12),
                child: SingleChildScrollView(
                  physics: BouncingScrollPhysics(),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.center,
                    children: [
                      SizedBox(height: dp.top + 60+12,),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.start,
                        children: [
                          Icon(
                            CupertinoIcons.wand_stars,
                            color: appColors.white,
                          ),
                          SizedBox(width: 10,),
                          Text(
                            'Generate a Noodl',
                            style: TextStyle(
                              fontFamily: 'NSansB',
                              fontSize: 22, 
                              color: appColors.white
                            ),
                          ),
                        ],
                      ),
                      SizedBox(height: 5,),
                      Text(
                        "Create a personalized learning journey tailored by AI—what we call a Noodl. Dive in, explore at your pace, and earn a unique NFT-based certificate once you complete it. It’s learning, leveled up.",
                        style: TextStyle(
                          color: appColors.white.withOpacity(0.5),
                          fontFamily: 'NSansM',
                          fontSize: 12
                        ),
                      ),
                      SizedBox(height: 12,),
                      NoodleGeneratorWidget(),
                      SizedBox(height: 12,),
                      provider.generatingTaskID != null
                        ? StreamBuilder(
                            stream: Stream.periodic(const Duration(seconds: 2))
                                .asyncMap((_) => APIservice.generatingNoodlProgress(
                                      taskID: provider.generatingTaskID!,
                                    )),
                                builder: (context, snapshot) {
                                  provider.logsDisplayScrollToBottom();
                                  if (snapshot.connectionState == ConnectionState.waiting && !snapshot.hasData) {
                                    return  LoadingStartingGenerationWidget();
                                  } else if (snapshot.hasError) {
                                    return Text('Error: ${snapshot.error}');
                                  } else if (snapshot.hasData) {
                                    // return Text(snapshot.data['progress'].toString());
                                  return LogsDisplay(items: snapshot.data['progress']);
                                  } 
                                  return const Text('No data yet');
                                  
                                },
                              )
                            : const SizedBox.shrink(),
                            // StartingGenerationWidget() 
                      // LogsDisplay(items: testData.logdisplaytestdata),
                      // SizedBox(height: 12,),
                      // Align(
                      //   alignment: Alignment.centerLeft,
                      //   child: Text(
                      //         'Your Generated Noodl',
                      //         style: TextStyle(
                      //           fontFamily: 'NSansB',
                      //           fontSize: 20, 
                      //           color: appColors.white
                      //         ),
                      //       ),
                      // ),
                      // SizedBox(height: 12,),
                      // NoodlButton(
                      //   title: '👨🏽‍⚖️ Law in India',
                      //   description: "A user-generated learning path about Law in India.",
                      // ),
                    ],
                  ),
                ),
              ),
              Topbar(
                leftIcon: CupertinoIcons.arrow_left,
                leftOnTap: () => Navigator.of(context).pop(),
              )
            ],
          ),
        ),
      ),
    );
  }
}