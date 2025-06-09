import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:frontend/constants/colors.dart' as appColors;
import 'package:frontend/providers/generate_page_provider.dart';
import 'package:frontend/services/services.dart';
import 'package:frontend/widgets/generate/generate_button.dart';
import 'package:frontend/widgets/generate/generator_textfeild.dart';
import 'package:provider/provider.dart';

class NoodleGeneratorWidget extends StatelessWidget {
  const NoodleGeneratorWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<GeneratePageProvider>(
      builder: (context, provider, child) => 
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
              'Enter a topic or skill you wish to learn—for example, ‘Introduction to Web3’ or ‘Machine Learning with Python’. Please avoid inappropriate content to ensure a meaningful learning experience.',
              style: TextStyle(
                fontFamily: 'NSansL',
                color: appColors.white.withOpacity(0.8),
                fontSize: 14
              ),
            ),
            SizedBox(height: 12,),
            GeneratorTextfeild(),
            SizedBox(height: 12,),
            GenerateButton(
              onTap: () async{
                dynamic response = await APIservice.generateNoodle(
                  prompt: "Law in India",
                  user_wallet_id: "heh123h813h18hd9u19jssj91"
                );
                response['message'] != 'E'?
                  provider.setGeneratingTaskID(response['task_id'])
                    :null;
                print(provider.generatingTaskID);
                
              },
            )
          ],
        ),
      ),
    );
  }
}