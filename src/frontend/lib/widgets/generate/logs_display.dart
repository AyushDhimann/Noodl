import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_svg/svg.dart';
import 'package:frontend/providers/generate_page_provider.dart';
import 'package:provider/provider.dart';
import 'package:frontend/constants/colors.dart' as appColors;

class LogsDisplay extends StatelessWidget {
  final List<dynamic> items;
  const LogsDisplay({super.key, required this.items});

  @override
  Widget build(BuildContext context) {
    Size size = MediaQuery.of(context).size;
    EdgeInsets dp = MediaQuery.of(context).padding;
    return Consumer<GeneratePageProvider>(
      builder: (context, provider, child) => 
      Container(
        margin: EdgeInsets.only(bottom: 12+dp.bottom),
        // padding: EdgeInsets.all(8),
        height: 250,
        width: size.width-24,
        decoration: BoxDecoration(
          borderRadius: BorderRadius.all(Radius.circular(12.5)),
          border: Border.all(width: 1, color: appColors.primary.withOpacity(0.25)),
          color: appColors.white.withOpacity(0.08)
        ),
        // child: ListView.builder(
        //   itemBuilder: (context, index) => Text(items[index].toString()),
        // ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              // color,
              height: 30,
              padding: EdgeInsets.symmetric(horizontal: 12),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.vertical(top: Radius.circular(12.5)),
                color: appColors.white.withOpacity(0.08)
              ),
              child: Row(
                children: [
                  SvgPicture.asset('assets/images/noodl_alt.svg', height: 20,),
                  SizedBox(width: 12,),
                  Text(
                    '- Generation logs - ',
                    style: TextStyle(
                      fontFamily: 'NSansL',
                      fontSize: 12,
                      color: appColors.white.withOpacity(0.7)
                    ),
                  ),
                ],
              ),
            ),
            Container(
              width: double.infinity,
              height: 1,
              color: appColors.black.withOpacity(0.75),
            ),
            SizedBox(
              height: 250 -30-2-2,
              child: Padding(
                padding: EdgeInsets.symmetric(horizontal: 8, vertical: 5),
                child: ListView(
                  scrollDirection: Axis.vertical,
                  controller: provider.logsDisplayScrollController,
                  children: [
                    ...items.map((i) => 
                      Text(
                        i['status'].toString(),
                        style: TextStyle(
                          fontFamily: 'MonolisaLI',
                          fontSize: 12,
                          color: appColors.white.withOpacity(0.8)
                        ),
                      ),
                    ),
                    SizedBox(height: 12,),
                    CupertinoActivityIndicator(),
                  ],
                ),
              ),
            ),
          ],
        ),
        // child: Text(items.toString())
      ),
    );
  }
}