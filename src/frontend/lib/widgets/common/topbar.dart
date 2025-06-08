import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:frontend/constants/colors.dart' as appColors;

class Topbar extends StatelessWidget {
  const Topbar({super.key});

  @override
  Widget build(BuildContext context) {
    EdgeInsets dp = MediaQuery.of(context).padding;
    return Container(
      padding: EdgeInsets.fromLTRB(12, dp.top, 12, 0),
      height: 60+dp.top,
      decoration: BoxDecoration(
        color: appColors.bgColor.withOpacity(0.85),
        border: Border(bottom: BorderSide(width: 1.5, color: appColors.primary.withOpacity(0.5)))
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.center,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          SvgPicture.asset('assets/images/noodl_alt.svg', height: 30,),
          InkWell(
            splashColor: appColors.white.withOpacity(0.75),
            borderRadius: BorderRadius.all(Radius.circular(20)),
            onTap: () {},
            child: SizedBox(
              width: 40,
              height: 40,
              child: Icon(CupertinoIcons.line_horizontal_3))
          )
        ],
      ),
    );
  }
}