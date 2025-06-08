import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:frontend/constants/colors.dart' as appColors;
import 'package:frontend/providers/quiz_page_provider.dart';
import 'package:provider/provider.dart';

class DidYouKnowScreen extends StatelessWidget {
  const DidYouKnowScreen({super.key});

  @override
  Widget build(BuildContext context) {
    Size size = MediaQuery.of(context).size;
    return Align(
      alignment: Alignment.topCenter,
      child: UnconstrainedBox(
        child: Container(
          padding: const EdgeInsets.all(12),
          margin: const EdgeInsets.symmetric(vertical: 36),
          width: size.width-36,
          decoration: BoxDecoration(
            color: appColors.primary.withOpacity(0.25),
            borderRadius: const BorderRadius.all(Radius.circular(12.5))
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                '💡 Did You Know?',
                style: TextStyle(
                  color: appColors.white,
                  fontSize: 20,
                  fontFamily: 'NSansB'
                ),
              ),
              SizedBox(height: 5,),
              Text(
                'India was the first country to nationalize its banks in 1969, bringing 14 major private banks under government control to ensure financial inclusion and rural development.',
                style: TextStyle(
                  color: appColors.white,
                  fontSize: 18,
                  fontFamily: 'NSansm'
                ),
              ),
              const SizedBox(height: 5,),
              Text(
                '📈 This move drastically increased the number of bank branches in rural areas and played a major role in improving access to credit across the country.',
                style: TextStyle(
                  color: appColors.white,
                  fontSize: 18,
                  fontFamily: 'NSansL'
                ),
              ),
              const SizedBox(height: 10,),
              Center(
                child: Consumer<QuizPageProvider>(
                  builder: (context, provider, child) => 
                  Material(
                    borderRadius: const BorderRadius.all(Radius.circular(25)),
                    color: appColors.white,
                    child: InkWell(
                      onTap: ()=>provider.goToNextQues(),
                      splashColor: Colors.black12,
                      borderRadius: const BorderRadius.all(Radius.circular(25)),
                      child: Container(
                        width: 50,
                        height: 50,
                        alignment: Alignment.center,
                        child: Icon(
                          CupertinoIcons.chevron_forward,
                          color: appColors.black,
                        ),
                      ),
                    ),
                  ),
                ),
              )
            ],
          ),
        ),
      ),
    );
  }
}