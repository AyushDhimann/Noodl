import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:frontend/providers/metamask_provider.dart';
import 'package:frontend/services/services.dart';
import 'package:frontend/widgets/common/topbar.dart';
import 'package:frontend/constants/colors.dart' as appColors;
import 'package:frontend/widgets/nft_page/nft_display_widget.dart';
import 'package:provider/provider.dart';

class NftPage extends StatelessWidget {
  const NftPage({super.key});

  @override
  Widget build(BuildContext context) {
    EdgeInsets dp = MediaQuery.of(context).padding;
    return PopScope(
      canPop: true,
      child: Scaffold(
        backgroundColor: appColors.bgColor,
        body: Consumer<MetaMaskProvider>(
          builder: (context, provider, child) => 
          Stack(
            alignment: Alignment.topCenter,
            children: [
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 12),
                child: SingleChildScrollView(
                  physics: BouncingScrollPhysics(),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      SizedBox(height: dp.top + 60 + 12),
                      Padding(
                        padding: EdgeInsetsGeometry.symmetric(horizontal: 0),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.start,
                          children: [
                            Icon(
                              CupertinoIcons.collections,
                              color: appColors.white,
                            ),
                            SizedBox(width: 10),
                            Text(
                              'Your NFTs',
                              style: TextStyle(
                                fontFamily: 'NSansB',
                                fontSize: 22,
                                color: appColors.white,
                              ),
                            ),
                          ],
                        ),
                      ),
                      SizedBox(height: 5),
                      Padding(
                        padding: EdgeInsetsGeometry.symmetric(horizontal: 0),
                        child: Text(
                          "Your shelf of Noodl flex! 🍜\nEvery NFT here is proof you crushed a Noodl.\nCollect, flex, repeat.",
                          style: TextStyle(
                            color: appColors.white.withOpacity(0.5),
                            fontFamily: 'NSansM',
                            fontSize: 12,
                          ),
                        ),
                      ),
                      SizedBox(height: 12),
                      FutureBuilder(
                        future: APIservice.fetchUserNFTs(walletAdd: provider.walletAddress!),
                        builder: (context, snapshot) {
                          if(snapshot.hasData){
                            print(snapshot.data!);
                            return Column(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                ...snapshot.data!.map((e) => NftDisplayWidget(data: e),)
                              ],
                            );
                          }
                          return CupertinoActivityIndicator();
                        },
                      ),
                    ],
                  ),
                ),
              ),
              Topbar(
                leftIcon: CupertinoIcons.arrow_left,
                leftOnTap: () => Navigator.of(context).pop(),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
