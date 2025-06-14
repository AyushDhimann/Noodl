import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:frontend/models/noodl_model.dart';
import 'package:frontend/providers/search_page_provider.dart';
import 'package:frontend/services/services.dart';
import 'package:frontend/widgets/common/topbar.dart';
import 'package:frontend/constants/colors.dart' as appColors;
import 'package:frontend/widgets/home/noodl_button.dart';
import 'package:frontend/widgets/search/search_textfeild.dart';
import 'package:provider/provider.dart';

class SearchPage extends StatelessWidget {
  const SearchPage({super.key});

  @override
  Widget build(BuildContext context) {
    Size size = MediaQuery.of(context).size;
    EdgeInsets dp = MediaQuery.of(context).padding;
    return GestureDetector(
      onTap: () => FocusScope.of(context).unfocus(),
      child: Scaffold(
        backgroundColor: appColors.bgColor,
        body: Consumer<SearchPageProvider>(
          builder: (context, provider, child) => Stack(
            children: [
              SingleChildScrollView(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      SizedBox(height: dp.top + 60 + 12),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.start,
                        children: [
                          Icon(CupertinoIcons.search, color: appColors.white),
                          SizedBox(width: 10),
                          Text(
                            'Search',
                            style: TextStyle(
                              fontFamily: 'NSansB',
                              fontSize: 22,
                              color: appColors.white,
                            ),
                          ),
                        ],
                      ),
                      SizedBox(height: 5),
                      Text(
                        "Search existing paths. Start learning. 🚀",
                        style: TextStyle(
                          color: appColors.white.withOpacity(0.5),
                          fontFamily: 'NSansM',
                          fontSize: 12,
                        ),
                      ),
                      SizedBox(height: 12),
                      SearchTextfeild(
                        textEditingController:  
                            provider.searchTextEditingController,
                      ),
                      SizedBox(height: 12),
                      Consumer<SearchPageProvider>(
                        builder: (context, provider, _) => provider.isLoading
                            ? Center(child: CupertinoActivityIndicator())
                            : Column(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  ...provider.results.map(
                                    (e) => NoodlButton(
                                      data: NoodlModel(
                                        createdAt: '',
                                        description: '',
                                        id: e.id,
                                        title: e.title,
                                        totalLevels: -1,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
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
