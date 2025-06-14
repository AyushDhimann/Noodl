import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_svg/svg.dart';
import 'package:frontend/models/user_nft_model.dart';
import 'package:frontend/constants/colors.dart' as appColors;
import 'package:frontend/services/copy_to_clipboard.dart';
import 'package:frontend/widgets/quiz/question_submit_button.dart';

class NftDisplayWidget extends StatelessWidget {
  final UserNftModel data;
  const NftDisplayWidget({super.key, required this.data});

  @override
  Widget build(BuildContext context) {
    Size size = MediaQuery.of(context).size;
    return Container(
      margin: EdgeInsets.only(bottom: 24),
      padding: EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: appColors.grey,
        borderRadius: BorderRadius.all(Radius.circular(12.5)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: size.width - 40,
            height: size.width - 40,
            margin: EdgeInsets.only(bottom: 12),
            decoration: BoxDecoration(
              color: appColors.grey,
              borderRadius: BorderRadius.all(Radius.circular(10)),
              // border: Border.all(width: 1, color: appColors.primary.withOpacity(0.8)),
              image: DecorationImage(
                image: NetworkImage(data.networkImageURL),
                fit: BoxFit.cover,
              ),
            ),
          ),
          Padding(
            padding: EdgeInsetsGeometry.symmetric(horizontal: 4),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  padding: EdgeInsets.symmetric(horizontal: 6, vertical: 3),
                  decoration: BoxDecoration(
                    // color: appColors.black,
                    border: Border.all(
                      width: 1,
                      color: appColors.white.withOpacity(0.25),
                    ),
                    borderRadius: BorderRadius.all(Radius.circular(10)),
                  ),
                  child: SvgPicture.asset(
                    'assets/images/noodl_alt.svg',
                    height: 22,
                  ),
                ),
                SizedBox(height: 5),
                Text(
                  data.learningPathTitle,
                  style: TextStyle(
                    fontFamily: 'NSansB',
                    fontSize: 20,
                    color: appColors.white,
                  ),
                ),
                SizedBox(height: 8),
                Container(
                  padding: EdgeInsets.symmetric(horizontal: 6, vertical: 3),
                  decoration: BoxDecoration(
                    color: appColors.primary.withOpacity(0.75),
                    borderRadius: BorderRadius.all(Radius.circular(10)),
                  ),
                  child: Text(
                    'NFT Contract Address',
                    style: TextStyle(
                      color: appColors.black,
                      fontFamily: 'NSansM',
                      fontSize: 14
                    ),
                  ),
                ),
                SizedBox(height: 5),
                Row(
                  children: [
                    Expanded(
                      child: SelectableText(
                        data.nftContractAdd,
                        maxLines: 1,
                        style: TextStyle(
                          color: appColors.white.withOpacity(0.7),
                          fontFamily: 'NSansM',
                          fontSize: 16,
                          // overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ),
                  ],
                ),
                SizedBox(height: 8,),
                Container(
                  padding: EdgeInsets.symmetric(horizontal: 6, vertical: 3),
                  decoration: BoxDecoration(
                    color: appColors.primary.withOpacity(0.75),
                    borderRadius: BorderRadius.all(Radius.circular(10)),
                  ),
                  child: Text(
                    'Token ID',
                    style: TextStyle(
                      color: appColors.black,
                      fontFamily: 'NSansM',
                      fontSize: 14
                    ),
                  ),
                ),
                SizedBox(height: 5),
                Row(
                  children: [
                    SelectableText(
                      data.tokenID.toString(),
                      maxLines: 1,
                      style: TextStyle(
                        color: appColors.white.withOpacity(0.7),
                        fontFamily: 'NSansM',
                        fontSize: 16,
                        // overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    SizedBox(width: 5,),
                    GestureDetector(
                      onTap: () {
                        copyToCliboard(context: context, copyThis: data.tokenID.toString());
                      },
                      child: Icon(
                        CupertinoIcons.square_fill_on_square_fill,
                        size: 18,
                        color: appColors.white,
                      ),
                    )
                  ],
                ),
                SizedBox(height: 12),
                Center(
                  child: Material(
                    borderRadius: BorderRadius.all(Radius.circular(100)),
                    color: appColors.white.withOpacity(1),
                    child: InkWell(
                    borderRadius: BorderRadius.all(Radius.circular(100)),
                    splashColor: appColors.black.withOpacity(0.25),
                      onTap: ()=>copyToCliboard(context: context, copyThis: data.nftContractAdd),
                      child: Container(
                        padding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.all(Radius.circular(100)),
                          // color: appColors.white,
                        ),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Icon(
                              CupertinoIcons.square_fill_on_square_fill,
                              color: appColors.black,
                              size: 18,
                            ),
                            SizedBox(width: 5,),
                            Text(
                              'Copy Contract Address',
                              style: TextStyle(
                                fontSize: 16, 
                                fontFamily: 'NSansM',
                                color: appColors.black
                              ),
                            ),
                            SizedBox(width: 5,),
                            Icon(
                              CupertinoIcons.square_fill_on_square_fill,
                              color: appColors.transparent,
                              size: 18,
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
          SizedBox(height: 4,)
          // Text('${data.pathID}'),
          // Text('${data.tokenID}'),
        ],
      ),
    );
  }
}
