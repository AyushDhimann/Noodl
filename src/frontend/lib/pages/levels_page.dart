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

class LevelsPage extends StatefulWidget {
  final NoodlModel noodlModel;
  const LevelsPage({super.key, required this.noodlModel});

  @override
  State<LevelsPage> createState() => _LevelsPageState();
}

class _LevelsPageState extends State<LevelsPage> {
  late Future<CoreNoodleDataModel?> _futureNoodlData;

  @override
  void initState() {
    super.initState();
    _futureNoodlData = _fetchNoodlData();
  }

  Future<CoreNoodleDataModel?> _fetchNoodlData() async {
    return await APIservice.fetchLevelsFromNoodl(pathID: widget.noodlModel.id);
  }

  Future<void> _refresh() async {
    setState(() {
      _futureNoodlData = _fetchNoodlData();
    });
  }

  @override
  Widget build(BuildContext context) {
    EdgeInsets dp = MediaQuery.of(context).padding;

    return Scaffold(
      backgroundColor: appColors.bgColor,
      body: Stack(
        children: [
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12),
            child: RefreshIndicator(
              edgeOffset: dp.top + 70,
              displacement: 20,
              color: appColors.primary,
              elevation: 0,
              onRefresh: _refresh,
              child: SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    SizedBox(height: dp.top + 60 + 12),
                    Text(
                      widget.noodlModel.title,
                      style: TextStyle(
                        fontFamily: 'NSansB',
                        fontSize: 22,
                        color: appColors.white,
                      ),
                    ),
                    SizedBox(height: 5),
                    widget.noodlModel.isComplete != null &&
                            widget.noodlModel.isComplete!
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
                                    builder: (context) => const NftPage(),
                                  ),
                                ),
                              ),
                            ],
                          )
                        : FutureBuilder<CoreNoodleDataModel?>(
                            future: _futureNoodlData,
                            builder: (context, snapshot) {
                              if (snapshot.connectionState ==
                                  ConnectionState.waiting) {
                                return const Padding(
                                  padding: EdgeInsets.only(top: 24),
                                  child: CupertinoActivityIndicator(),
                                );
                              }

                              if (!snapshot.hasData || snapshot.data == null) {
                                return const Padding(
                                  padding: EdgeInsets.only(top: 24),
                                  child: Text(
                                    "Something went wrong. Please try again.",
                                    style: TextStyle(color: Colors.white),
                                  ),
                                );
                              }

                              final noodlData = snapshot.data!;
                              return Column(
                                mainAxisSize: MainAxisSize.min,
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    noodlData.longDescription,
                                    style: TextStyle(
                                      color: appColors.white.withOpacity(0.75),
                                      fontFamily: 'NSansL',
                                      fontSize: 14,
                                    ),
                                  ),
                                  const SizedBox(height: 12),
                                  ...noodlData.levels.map(
                                    (levelModel) =>
                                        LevelWidget(data: levelModel),
                                  ),
                                ],
                              );
                            },
                          ),
                  ],
                ),
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
