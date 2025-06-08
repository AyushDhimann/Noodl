import 'package:flutter/material.dart';
import 'package:frontend/constants/colors.dart' as appColors;

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    Size size = MediaQuery.of(context).size;
    EdgeInsets dp = MediaQuery.of(context).padding;
    return Scaffold(
      backgroundColor: appColors.bgColor,
      body: SizedBox(
        
      ),
    );
  }
}