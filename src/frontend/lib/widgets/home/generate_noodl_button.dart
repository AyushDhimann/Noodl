import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:frontend/constants/colors.dart' as appColors;

class GenerateNoodlButton extends StatelessWidget {
  const GenerateNoodlButton({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.all(12),
      margin: EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: appColors.primary.withOpacity(1),
        borderRadius: BorderRadius.all(Radius.circular(12.5))
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.start,
            children: [
              Icon(
                CupertinoIcons.wand_stars,
                color: appColors.black,
              ),
              SizedBox(width: 10,),
              Text(
                'Generate a Noodl',
                style: TextStyle(
                  fontFamily: 'NSansB',
                  fontSize: 22, 
                  color: appColors.black
                ),
              ),
            ],
          ),
          SizedBox(height: 8,),
          Text(
            'Generate a learning path of your choice with AI and earn an NFT-based certificate upon completing a Noodl.',
            style: TextStyle(
              fontFamily: 'NSansL',
              color: appColors.black,
              fontSize: 14
            ),
          ),
          SizedBox(height: 8,),
          Align(
            alignment: Alignment.centerRight,
            child: Material(
              borderRadius: BorderRadius.all(Radius.circular(100)),
              color: appColors.black.withOpacity(0.1),
              child: InkWell(
                borderRadius: BorderRadius.all(Radius.circular(100)),
                splashColor: appColors.white.withOpacity(0.5),
                onTap: () {
                },
                child: Container(
                  padding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        'Get started',
                        style: TextStyle(
                          fontFamily: 'NSansM',
                          fontSize: 16, 
                          color: appColors.black
                        ),
                      ),
                      SizedBox(width: 5,),
                      Icon(
                        CupertinoIcons.arrow_right,
                        color: appColors.black,
                        size: 18,
                      )
                    ],
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}