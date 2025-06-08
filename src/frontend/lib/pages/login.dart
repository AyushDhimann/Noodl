import 'package:flutter/material.dart';
import 'package:flutter_svg/svg.dart';
import 'package:frontend/constants/colors.dart' as appColors;
import 'package:frontend/services/metamask_service.dart';
import 'package:provider/provider.dart';

class LoginPage extends StatelessWidget {
  const LoginPage({super.key});

  @override
  Widget build(BuildContext context) {
    EdgeInsets dp = MediaQuery.of(context).padding;
    Size size = MediaQuery.of(context).size;
    return Scaffold(
      backgroundColor: appColors.bgColor,
      body: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SizedBox(height: dp.top+24,),
            Center(child: SvgPicture.asset('assets/images/noodl.svg', width: size.width/3,)),
            const SizedBox(height: 36,),
            Expanded(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '🍜 Welcome to noodl.',
                    style: TextStyle(
                      fontFamily: 'NSansB',
                      fontSize: 22,
                      color: appColors.white
                    ),
                  ),
                  Text(
                    'Learn anything and everything the smart way — through short bursts, fun quizzes, and real rewards.',
                    style: TextStyle(
                      fontFamily: 'NSansL',
                      fontSize: 18,
                      color: appColors.white
                    ),
                  ),
                  const SizedBox(height: 20,),
                  Text(
                    '🧠 Powered by Web3',
                    style: TextStyle(
                      fontFamily: 'NSansB',
                      fontSize: 22,
                      color: appColors.white
                    ),
                  ),
                  Text(
                    'Noodl uses secure blockchain technology to give you true ownership of your progress, achievements, and rewards.',
                    style: TextStyle(
                      fontFamily: 'NSansL',
                      fontSize: 18,
                      color: appColors.white
                    ),
                  ),
                  const SizedBox(height: 20,),
                  Text(
                    '🦊 Sign in with MetaMask',
                    style: TextStyle(
                      fontFamily: 'NSansB',
                      fontSize: 22,
                      color: appColors.white
                    ),
                  ),
                  Text(
                    'To keep your data safe and your learning profile truly yours, we use MetaMask — a trusted Web3 wallet that lets you sign in without passwords.\n🎯 No emails. No third parties. Just you and your wallet.',
                    style: TextStyle(
                      fontFamily: 'NSansL',
                      fontSize: 18,
                      color: appColors.white
                    ),
                  ),
                ],
              )
            ),
            Center(
              child: Material(
              borderRadius: const BorderRadius.all(Radius.circular(12.5)),
              color: appColors.bgColor,
              child: InkWell(
                splashColor: Colors.black12,
              borderRadius: const BorderRadius.all(Radius.circular(12.5)),
                onTap: ()=>{},
                child: Container(
                  height: 50,
                  width: size.width-24,
                  decoration: BoxDecoration(
                    borderRadius: const BorderRadius.all(Radius.circular(12.5)),
                    border: Border.all(width: 1.5, color: appColors.white)
                  ),
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                  child:  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      SvgPicture.asset('assets/images/metamask.svg', height: 20,),
                      Text(
                        'Connect with MetaMask',
                        style: TextStyle(
                          color: appColors.white,
                          fontSize: 16,
                          fontFamily: 'NSansM'
                        ),
                      ),
                      Opacity(opacity: 0,child: SvgPicture.asset('assets/images/metamask.svg', height: 20,))
                    ],
                  ),
                ),
              ),
                                ),
            ),
            SizedBox(
              height: dp.bottom+12,
            )
          ],
        ),
      ),
    );
  }
}