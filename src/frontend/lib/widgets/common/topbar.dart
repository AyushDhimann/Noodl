import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:frontend/constants/colors.dart' as appColors;
import 'package:frontend/providers/metamask_provider.dart';
import 'package:provider/provider.dart';

class Topbar extends StatelessWidget {
  const Topbar({super.key});

  @override
  Widget build(BuildContext context) {
    EdgeInsets dp = MediaQuery.of(context).padding;
    final metaMaskProvider = Provider.of<MetaMaskProvider>(context, listen: false);

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
          PopupMenuButton<String>(
            onSelected: (value) {
              if (value == 'disconnect') {
                metaMaskProvider.disconnect();
              }
            },
            color: appColors.grey,
            icon: Icon(CupertinoIcons.line_horizontal_3, color: appColors.white),
            itemBuilder: (BuildContext context) => <PopupMenuEntry<String>>[
              PopupMenuItem<String>(
                value: 'wallet',
                child: Text(
                  'Wallet: ${metaMaskProvider.walletAddress?.substring(0, 6)}...${metaMaskProvider.walletAddress?.substring(metaMaskProvider.walletAddress!.length - 4)}',
                  style: TextStyle(fontFamily: 'NSansM', color: appColors.white),
                ),
                enabled: false, // Make it not clickable
              ),
              const PopupMenuDivider(),
              PopupMenuItem<String>(
                value: 'disconnect',
                child: Text(
                  'Disconnect',
                  style: TextStyle(fontFamily: 'NSansM', color: appColors.red),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}