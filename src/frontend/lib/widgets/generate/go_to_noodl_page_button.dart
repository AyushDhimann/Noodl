import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:frontend/pages/user_noodls.dart';
import 'package:frontend/constants/colors.dart' as appColors;
import 'package:frontend/providers/generate_page_provider.dart';
import 'package:provider/provider.dart';

class GoToNoodlPageButton extends StatelessWidget {
  const GoToNoodlPageButton({super.key});

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: Alignment.centerRight,
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 12),
        child: Material(
          color: appColors.primary,
          borderRadius: BorderRadius.all(Radius.circular(100)),
          child: InkWell(
            borderRadius: BorderRadius.all(Radius.circular(100)),
          
            onTap: () {
              // Navigator.of(context).pushReplacement(MaterialPageRoute(builder: (context) => UserNoodlsPage(),));
              FocusScope.of(context).unfocus();
              Navigator.of(context).push(MaterialPageRoute(builder: (context) => UserNoodlsPage(),));
              Provider.of<GeneratePageProvider>(context, listen: false).nullGenereatingTaskID();
              },
            child: Container(
              padding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    'Go to Noodls Page',
                    style: TextStyle(
                      fontFamily: 'NSansM',
                      fontSize: 14,
                      color: appColors.black
                    ),
                  ),
                  SizedBox(width: 5,),
                  Icon(
                    CupertinoIcons.arrow_right,
                    size: 18,
                    color: appColors.black,
                  )
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}