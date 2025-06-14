import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:frontend/constants/colors.dart' as appColors;

void copyToCliboard({
  required BuildContext context,
  required String copyThis,
}) async {
  // final contractAdd = data.nftContractAdd;
  Size size = MediaQuery.of(context).size;
  await Clipboard.setData(ClipboardData(text: copyThis));
  if (context.mounted) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        // margin: EdgeInsets.only(bottom: size.height/2),
        behavior: SnackBarBehavior.floating,
        backgroundColor: appColors.transparent,
        duration: Duration(seconds: 2),
        elevation: 0,
        width: size.width / 2,
        content: Center(
          child: Container(
            padding: EdgeInsets.all(8),
            alignment: Alignment.center,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.all(Radius.circular(100)),
              color: appColors.white.withOpacity(1),
            ),
            child: Text(
              'Copied!',
              style: TextStyle(
                fontSize: 16,
                color: appColors.black,
                fontFamily: 'NSansM',
              ),
            ),
          ),
        ),
      ),
    );
  }
}
