import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:frontend/constants/colors.dart' as appColors;
import 'package:frontend/models/noodl_model.dart';
import 'package:frontend/pages/login.dart';
import 'package:frontend/pages/search.dart';
import 'package:frontend/pages/user_noodls.dart';
import 'package:frontend/providers/metamask_provider.dart';
import 'package:frontend/services/services.dart';
import 'package:frontend/widgets/common/topbar.dart';
import 'package:frontend/widgets/home/bottom_options_dialog.dart';
import 'package:frontend/widgets/home/empty_your_noodls.dart';
import 'package:frontend/widgets/home/generate_noodl_button.dart';
import 'package:frontend/widgets/home/heading_widget.dart';
import 'package:frontend/widgets/home/noodl_button.dart';
import 'package:frontend/widgets/home/view_all_noodls_button.dart';
import 'package:provider/provider.dart';

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    Size size = MediaQuery.of(context).size;
    EdgeInsets dp = MediaQuery.of(context).padding;
    return Scaffold(
      backgroundColor: appColors.bgColor,
      body: Stack(
        children: [
          RefreshIndicator(
            edgeOffset: dp.top + 70,
            displacement: 20,
            color: appColors.primary,
            elevation: 0,
            onRefresh: () async {
              await Future.delayed(Duration(seconds: 1));

              context.mounted
                  ? Navigator.of(context).pushReplacement(
                      PageRouteBuilder(
                        pageBuilder: (context, a1, a2) => HomePage(),
                        transitionDuration: Duration.zero,
                        reverseTransitionDuration: Duration.zero,
                      ),
                    )
                  : null;
              return;
            },

            child: ListView(
              padding: EdgeInsets.zero,
              // crossAxisAlignment: CrosAxisAlignment.center,
              children: [
                SizedBox(height: dp.top + 60),
                SizedBox(height: 12),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // SizedBox(height: 12,),
                      FutureBuilder(
                        future: APIservice.getUserNoodls(
                          walletAdd: Provider.of<MetaMaskProvider>(
                            context,
                            listen: false,
                          ).walletAddress!,
                          // ??"0x718fafb76e1631f5945bf58104f3b81d9588819b",
                          // remove this
                          // walletAdd: Provider.of<MetaMaskProvider>(context, listen: false).walletAddress!,
                          limit: 2,
                        ),
                        builder: (context, snapshot) {
                          return snapshot.hasData &&
                                  (snapshot.data! as List).isNotEmpty
                              ? Column(
                                  mainAxisSize: MainAxisSize.min,
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Row(
                                      mainAxisAlignment:
                                          MainAxisAlignment.spaceBetween,
                                      crossAxisAlignment:
                                          CrossAxisAlignment.start,
                                      children: [
                                        HeadingWidget(
                                          heading: 'Your Noodls',
                                          subHeading:
                                              'Your learning paths appear here.',
                                        ),
                                        ViewAllNoodlsButton(
                                          onTap: () =>
                                              Navigator.of(context).push(
                                                MaterialPageRoute(
                                                  builder: (context) =>
                                                      UserNoodlsPage(),
                                                ),
                                              ),
                                        ),
                                      ],
                                    ),
                                    ...snapshot.data.map(
                                      (e) => NoodlButton(data: e),
                                    ),
                                    // ShowAllNoodlsButton()
                                  ],
                                )
                              : Column(
                                  mainAxisSize: MainAxisSize.min,
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    HeadingWidget(
                                      heading: 'Your Noodls',
                                      subHeading:
                                          'Your learning paths appear here.',
                                    ),
                                    EmptyYourNoodls(),
                                  ],
                                );
                        },
                      ),

                      // SizedBox(height: 12,),
                      GenerateNoodlWidget(),
                      HeadingWidget(
                        heading: 'Community Noodls',
                        subHeading:
                            'Community Noodls refer to popular learning paths previously generated by other users.',
                      ),
                      FutureBuilder(
                        future: APIservice.getCommunityNoodls(),
                        builder: (context, snapshot) {
                          return snapshot.hasData
                              ? Column(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    ...snapshot.data.map(
                                      (e) => NoodlButton(data: e),
                                    ),
                                    SizedBox(height: 12),
                                    SizedBox(height: 12),
                                  ],
                                )
                              : Center(child: CupertinoActivityIndicator());
                        },
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          Topbar(
            rightIcon: CupertinoIcons.line_horizontal_3,
            rightOnTap: () {
              showBottomOptionsDialog(context: context);
            },
            searchIcon: CupertinoIcons.search,
            searchOnTap: () => Navigator.of(
              context,
            ).push(MaterialPageRoute(builder: (context) => SearchPage())),
          ),
        ],
      ),
    );
  }
}
