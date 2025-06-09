import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:frontend/constants/colors.dart' as appColors;

class Topbar extends StatelessWidget {
  final IconData? leftIcon;
  final VoidCallback? leftOnTap;
  final IconData? rightIcon;
  final VoidCallback? rightOnTap;

  const Topbar({super.key, this.leftIcon, this.leftOnTap, this.rightIcon, this.rightOnTap});

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
          leftIcon==null?
            SvgPicture.asset('assets/images/noodl_alt.svg', height: 30,)
            : TopbarButton(
              icon: leftIcon,
              onTap: leftOnTap,
            ),

          TopbarButton(
            icon: rightIcon,
            onTap: rightOnTap,
          )
        ],
      ),
    );
  }
}

class TopbarButton extends StatelessWidget {
  final IconData? icon;
  final VoidCallback? onTap;
  const TopbarButton({super.key, this.icon, this.onTap});

  @override
  Widget build(BuildContext context) {
    return InkWell(
      splashColor: appColors.white.withOpacity(0.85),
      borderRadius: BorderRadius.all(Radius.circular(20)),
      onTap: onTap,
      child: SizedBox(
        width: 40,
        height: 40,
        child: Icon(icon)
      )
    );
  }
}