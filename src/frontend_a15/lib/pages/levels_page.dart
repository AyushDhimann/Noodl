import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:frontend/models/core_level_model.dart';
import 'package:frontend/models/noodl_model.dart';
import 'package:frontend/constants/colors.dart' as appColors;
import 'package:frontend/pages/nft_page.dart';
import 'package:frontend/services/services.dart';
import 'package:frontend/widgets/common/topbar.dart';
import 'package:frontend/widgets/levels_page/level_widget.dart';
import 'package:frontend/widgets/quiz/results_page_button.dart';

class LevelsPage extends StatelessWidget {
  final NoodlModel noodlModel;
  const LevelsPage({super.key, required this.noodlModel});

  @override
  Widget build(BuildContext context) {
    EdgeInsets dp = MediaQuery.of(context).padding;
    Size size = MediaQuery.of(context).size;
    return Scaffold(
      backgroundColor: appColors.bgColor,
      body: Stack(
        children: [
          Padding(
            padding: EdgeInsetsGeometry.symmetric(horizontal: 12),
            child: SingleChildScrollView(
              physics: BouncingScrollPhysics(),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  SizedBox(height: dp.top + 60 + 12),
                  Text(
                    noodlModel.title,
                    style: TextStyle(
                      fontFamily: 'NSansB',
                      fontSize: 22,
                      color: appColors.white,
                    ),
                  ),
                  // SizedBox(height: 5,),
                  // Align(
                  //   alignment: Alignment.centerLeft,
                  //   child: Text(
                  //     '#${noodlModel.id}',
                  //     style: TextStyle(
                  //       color: appColors.primary.withOpacity(1),
                  //       fontFamily: 'NSansB',
                  //       fontSize: 16
                  //     ),
                  //   ),
                  // ),
                  SizedBox(height: 5),
                  noodlModel.isComplete != null && noodlModel.isComplete!
                      ? Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Text(
                              "😌Already done with this Noodl! Wanna flex? Check your NFT on the NFTs page below.",
                              style: TextStyle(
                                color: appColors.white.withOpacity(0.75),
                                fontFamily: 'NSansL',
                                fontSize: 14,
                              ),
                            ),
                            ResultsPageButton(
                              text: 'To My NFT Stash',
                              onTap: () => Navigator.of(context).push(
                                MaterialPageRoute(
                                  builder: (context) => NftPage(),
                                ),
                              ),
                            ),
                          ],
                        )
                      : FutureBuilder(
                          future: APIservice.fetchLevelsFromNoodl(
                            pathID: noodlModel.id,
                          ),
                          builder: (context, snapshot) {
                            return snapshot.hasData
                                ? Column(
                                    mainAxisSize: MainAxisSize.min,
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        snapshot.data!.longDescription,
                                        style: TextStyle(
                                          color: appColors.white.withOpacity(
                                            0.75,
                                          ),
                                          fontFamily: 'NSansL',
                                          fontSize: 14,
                                        ),
                                      ),
                                      SizedBox(height: 12),
                                      ...snapshot.data!.levels.map(
                                        (levelModel) =>
                                            LevelWidget(data: levelModel),
                                      ),
                                    ],
                                  )
                                : Padding(
                                    padding: const EdgeInsets.only(top: 24),
                                    child: CupertinoActivityIndicator(),
                                  );
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
    );
  }
}
