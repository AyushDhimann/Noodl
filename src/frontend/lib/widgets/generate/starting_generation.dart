import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:frontend/constants/colors.dart' as appColors;

class LoadingStartingGenerationWidget extends StatelessWidget {
  const LoadingStartingGenerationWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Container(
        padding: EdgeInsets.symmetric(vertical: 12, horizontal: 8),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.all(Radius.circular(12.5)),
          color: appColors.white.withOpacity(0.08),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            CupertinoActivityIndicator(radius: 15,),
            SizedBox(height: 12,),
            Text(
              'Generating',
              style: TextStyle(
                color: appColors.white.withOpacity(0.5),
                fontSize: 12,
              ),
            )
          ],
        ),
      ),
    );
  }
}