import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:frontend/constants/colors.dart' as appColors;

class NoodlButton extends StatelessWidget {
  final String title;
  final String description;
  const NoodlButton({super.key, required this.title, required this.description});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(bottom: 12),
      child: Material(
        borderRadius: BorderRadius.all(Radius.circular(12.5)),
        color: Colors.white.withOpacity(0.08),
        child: InkWell(
        borderRadius: BorderRadius.all(Radius.circular(12.5)),
          onTap: () {
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
                      'noodl.',
                      style: TextStyle(
                        color: appColors.white.withOpacity(0.03),
                        fontFamily: 'MonolisaBB',
                        letterSpacing: -1,
                        height: 1
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
                        // Text(
                        //   '#1',
                        //   style: TextStyle(
                        //     fontSize: 14,
                        //     fontFamily: 'NSansM',
                        //     color: appColors.white.withOpacity(0.5)
                        //   ),
                        // ),
                        // SizedBox(height: 5,),
                        Text(
                          title,
                          style: TextStyle(
                            color: appColors.white,
                            fontSize: 20,
                            fontFamily: 'NSansB'
                          ),
                        ),
                        SizedBox(height: 5,),
                        Text(
                          description,
                          style: TextStyle(
                            color: appColors.white,
                            fontSize: 14,
                            fontFamily: 'NSansL'
                          ),
                        ),
                        SizedBox(height: 5,),
                        Align(
                          alignment: Alignment.centerRight,
                          child: Icon(
                            CupertinoIcons.arrow_right,
                            color: appColors.white,
                          ),
                        )
                      ],
                    ),
                  ),
                )
              ],
            ),
          ),
        ),
      ),
    );
  }
}