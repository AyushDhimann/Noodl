import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_svg/svg.dart';
import 'package:frontend/constants/colors.dart' as appColors;
import 'package:frontend/pages/login.dart';
import 'package:frontend/pages/nft_page.dart';
import 'package:frontend/providers/login_page_provider.dart';
import 'package:frontend/providers/metamask_provider.dart';
import 'package:frontend/services/copy_to_clipboard.dart';
import 'package:frontend/services/services.dart';
import 'package:frontend/widgets/quiz/results_page_button.dart';
import 'package:provider/provider.dart';

void showBottomOptionsDialog({required BuildContext context}) {
  showModalBottomSheet(
    context: context,
    barrierColor: appColors.black.withOpacity(0.7),
    backgroundColor: Colors.transparent,
    builder: (context) {
      EdgeInsets dp = MediaQuery.of(context).padding;
      Size size = MediaQuery.of(context).size;
      return Scaffold(
        backgroundColor: Colors.transparent,
        body: Consumer<LoginPageProvider>(
          builder: (context, provider, child) => 
          Align(
            alignment: Alignment.bottomCenter,
            child: Stack(
              children: [
                Container(
                  width: double.infinity,
                  margin: EdgeInsets.symmetric(horizontal: 5),
                  padding: EdgeInsets.fromLTRB(20, 8, 20, dp.bottom + 5),
                  decoration: BoxDecoration(
                    color: appColors.grey,
                    borderRadius: BorderRadius.vertical(top: Radius.circular(12.5)),
                    border: BoxBorder.fromLTRB(
                      left: BorderSide(
                        width: 1,
                        color: appColors.primary.withOpacity(0.5),
                      ),
                      right: BorderSide(
                        width: 1,
                        color: appColors.primary.withOpacity(0.5),
                      ),
                      top: BorderSide(
                        width: 1,
                        color: appColors.primary.withOpacity(0.5),
                      ),
                    ),
                  ),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Container(
                        width: 40,
                        height: 5,
                        margin: EdgeInsets.only(bottom: 12),
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.all(Radius.circular(100)),
                          color: appColors.primary.withOpacity(0.8),
                          // color: appColors.white.withOpacity(0.4),
                        ),
                      ),
                      SvgPicture.asset('assets/images/noodl_alt.svg', height: 25),
                      Text(
                        'Version Ramen (0.1)',
                        style: TextStyle(
                          fontSize: 12,
                          color: appColors.white.withOpacity(0.4),
                          fontFamily: 'NSansL',
                        ),
                      ),
                      SizedBox(height: 12),
                      FutureBuilder(
                        future: APIservice.fetchUserNameCountry(
                          walletAdd: Provider.of<MetaMaskProvider>(
                            context,
                            listen: false,
                          ).walletAddress!,
                          // '0x718fafb76e1631f5945bf58104f3b81d9588819b',
                        ),
                        builder: (context, snapshot) => snapshot.hasData
                            ? Column(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Row(
                                    children: [
                                      Icon(CupertinoIcons.person_fill, size: 18),
                                      SizedBox(width: 5),
                                      Expanded(
                                        child: Text(
                                          snapshot.data!['name'],
                                          overflow: TextOverflow.fade,
                                          style: TextStyle(
                                            color: appColors.white.withOpacity(0.85),
                                            fontFamily: 'NSansB',
                                            fontSize: 16,
                                          ),
                                        ),
                                      ),
                                    ],
                                  ),
                                  SizedBox(height: 12),
                                  Row(
                                    children: [
                                      Icon(CupertinoIcons.map_pin_ellipse, size: 18),
                                      SizedBox(width: 5),
                                      Expanded(
                                        child: Text(
                                          snapshot.data!['country'],
                                          overflow: TextOverflow.fade,
                                          style: TextStyle(
                                            color: appColors.white.withOpacity(0.85),
                                            fontFamily: 'NSansB',
                                            fontSize: 16,
                                          ),
                                        ),
                                      ),
                                    ],
                                  ),
                                ],
                              )
                            : SizedBox(
                                height: 58,
                                child: CupertinoActivityIndicator(),
                              ),
                      ),
                
                      SizedBox(height: 12),
                      Row(
                        children: [
                          Icon(CupertinoIcons.number, size: 18),
                          SizedBox(width: 5),
                          Expanded(
                            child: Text(
                              Provider.of<MetaMaskProvider>(
                                context,
                                listen: false,
                              ).walletAddress!,
                              // '0x718fafb76e1631f5945bf58104f3b81d9588819b',
                              overflow: TextOverflow.ellipsis,
                              maxLines: 1,
                              style: TextStyle(
                                color: appColors.white.withOpacity(0.85),
                                fontFamily: 'NSansM',
                                fontSize: 16,
                              ),
                            ),
                          ),
                          SizedBox(width: 5),
                          GestureDetector(
                            onTap: () => copyToCliboard(
                              context: context,
                              copyThis: Provider.of<MetaMaskProvider>(
                                context,
                                listen: false,
                              ).walletAddress!,
                            ),
                            child: Icon(
                              CupertinoIcons.square_fill_on_square_fill,
                              size: 18,
                            ),
                          ),
                        ],
                      ),
                      // SizedBox(height: 12,),
                      Align(
                        alignment: Alignment.centerLeft,
                        child: SingleChildScrollView(
                          scrollDirection: Axis.horizontal,
                          padding: EdgeInsets.zero,
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.center,
                            children: [
                              ResultsPageButton(
                                text: 'My NFTs',
                                onTap: () {
                                  Navigator.of(context).pushReplacement(
                                    MaterialPageRoute(
                                      builder: (context) => NftPage(),
                                    ),
                                  );
                                },
                              ),
                              SizedBox(width: 12),
                              ResultsPageButton(
                                text: 'Logout',
                                altStyling: true,
                                onTap: () async{
                                  // provider.loggingOutTrue();
                                  Navigator.of(context).pop();
                                  await Provider.of<MetaMaskProvider>(
                                    context,
                                    listen: false,
                                  ).logout();
                                  //   ..pushReplacement(
                                  //     MaterialPageRoute(
                                  //       builder: (context) => LoginPage(),
                                  //     ),
                                  //   );
                                },
                              ),
                            ],
                          ),
                        ),
                      ),
                      SizedBox(height: 12),
                      Text(
                        'Cooked with ❤️ by Ayush & Parth 🍜',
                        style: TextStyle(
                          fontSize: 12,
                          color: appColors.white.withOpacity(0.4),
                          fontFamily: 'NSansL',
                        ),
                      ),
                    ],
                  ),
                ),
                
                provider.loggingOut?
                Center(child: CupertinoActivityIndicator(),):SizedBox.shrink()
              ],
            ),
          ),
        ),
      );
    },
  );
}
