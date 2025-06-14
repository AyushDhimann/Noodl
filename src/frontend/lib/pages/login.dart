import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:frontend/constants/colors.dart' as appColors;
import 'package:frontend/providers/login_page_provider.dart';
import 'package:frontend/providers/metamask_provider.dart';
import 'package:frontend/widgets/generate/generator_textfeild.dart';
import 'package:frontend/widgets/search/search_textfeild.dart';
import 'package:provider/provider.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final TextEditingController _walletController = TextEditingController();

  Widget _buildLoadingScreen(BuildContext context) {
    return Scaffold(
      backgroundColor: appColors.bgColor,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(color: appColors.primary),
            const SizedBox(height: 24),
            Text(
              'Connecting to MetaMask...',
              style: TextStyle(
                color: appColors.white,
                fontSize: 18,
                fontFamily: 'NSansM',
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Please approve the connection in your wallet.',
              style: TextStyle(
                color: appColors.white.withOpacity(0.6),
                fontSize: 14,
                fontFamily: 'NSansL',
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final metaMaskProvider = context.watch<MetaMaskProvider>();
    // final loginPageProvider = context.watch<LoginPageProvider>();
    final size = MediaQuery.of(context).size;
    final dp = MediaQuery.of(context).padding;

    if (metaMaskProvider.isConnecting) {
      return _buildLoadingScreen(context);
    }

    return GestureDetector(
      onTap: () => FocusScope.of(context).unfocus(),
      child: Scaffold(
        backgroundColor: appColors.bgColor,
        body: Column(
          children: [
            Expanded(
              flex: 3,
              child: Stack(
                children: [
                  Container(
                    decoration: BoxDecoration(
                      image: DecorationImage(
                        image: AssetImage('assets/images/noodl_bg.jpg'),
                        fit: BoxFit.cover,
                      ),
                    ),
                    child: Center(
                      child: SvgPicture.asset(
                        'assets/images/noodl_alt.svg',
                        width: size.width / 3.5,
                      ),
                    ),
                  ),
                  Container(
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [appColors.bgColor, appColors.transparent],
                        begin: Alignment.bottomCenter,
                        end: Alignment.center,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            Expanded(
              flex: 2,
              child: Consumer<LoginPageProvider>(
                builder: (context, provider, child) =>
                PageView(
                  // physics: NeverScrollableScrollPhysics(),
                  controller: provider.loginPageController,
                  children: [
                    SizedBox(
                      width: size.width,
                      child: Padding(
                        padding: EdgeInsetsGeometry.symmetric(horizontal: 12),
                        child: SingleChildScrollView(
                          physics: BouncingScrollPhysics(),
                          child: Column(
                            // mainAxisSize: MainAxisSize.min,
                            crossAxisAlignment: CrossAxisAlignment.start,
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              // const SizedBox(height: 24),
                              Column(
                                mainAxisSize: MainAxisSize.min,
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    'Noodl - Learn, Prove, Own.',
                                    style: TextStyle(
                                      color: appColors.white,
                                      fontFamily: 'NSansB',
                                      fontSize: 20,
                                    ),
                                  ),
                                  SizedBox(height: 5),
                                  Text(
                                    'Learning doesn’t have to be boring. Noodl turns your knowledge journey into a gamified experience. Master levels, prove your progress, and collect unique NFTs as trophies of your learning. It’s smart. It’s fun. It’s yours to earn.',
                                    style: TextStyle(
                                      color: appColors.white.withOpacity(0.75),
                                      fontFamily: 'NSansL',
                                      fontSize: 14,
                                    ),
                                  ),
                                ],
                              ),
                              SizedBox(height: 0.07 * size.height),

                              // SizedBox(height: 0.1*size.height,),
                              Column(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  _buildMetaMaskButton(
                                    context,
                                    metaMaskProvider,
                                    size,
                                  ),
                                  SizedBox(height: 5),
                                  GestureDetector(
                                    onTap: () => provider.goNextPage(),
                                    child: Padding(
                                      padding: const EdgeInsets.all(7),
                                      child: Text(
                                        'Android 15 or above?',
                                        style: TextStyle(
                                          color: appColors.primary,
                                          fontSize: 14,
                                          fontFamily: 'NSansL',
                                        ),
                                      ),
                                    ),
                                  ),
                                  SizedBox(height: dp.bottom),
                                ],
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                    SizedBox(
                      width: size.width,
                      child: SingleChildScrollView(
                        physics: BouncingScrollPhysics(),
                        child: Column(
                          // mainAxisSize: MainAxisSize.min,
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            // const SizedBox(height: 24),
                            Padding(
                              padding: const EdgeInsets.only(
                                bottom: 12,
                                left: 12,
                                right: 12,
                              ),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                // mainAxisSize: MainAxisSize.min,
                                children: [
                                  Text(
                                    'Legacy Login',
                                    style: TextStyle(
                                      color: appColors.white,
                                      fontFamily: 'NSansB',
                                      fontSize: 20,
                                    ),
                                  ),
                                  SizedBox(height: 5),
                                  Text(
                                    '\'noodl.\' doesn\'t support MetaMask login on Android 15 and above. Use this option to log in by manually entering your wallet address.',
                                    style: TextStyle(
                                      color: appColors.white.withOpacity(0.75),
                                      fontFamily: 'NSansL',
                                      fontSize: 14,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            SizedBox(height: 0.03 * size.height),
                            Column(
                              children: [
                                _buildManualWalletField(
                                  context,
                                  metaMaskProvider,
                                  size,
                                ),
                                SizedBox(height: 5,),
                                GestureDetector(
                                  onTap: () => provider.goPrevPage(),
                                  child: Padding(
                                    padding: const EdgeInsets.all(7),
                                    child: Text(
                                      'MetaMask Login',
                                      style: TextStyle(
                                        color: appColors.primary,
                                        fontSize: 14,
                                        fontFamily: 'NSansL',
                                      ),
                                    ),
                                  ),
                                ),
                                SizedBox(height: dp.bottom),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionTitle(String text) {
    return Text(
      text,
      style: TextStyle(
        fontFamily: 'NSansB',
        fontSize: 20,
        color: appColors.white,
      ),
    );
  }

  Widget _buildSectionText(String text) {
    return Text(
      text,
      style: TextStyle(
        fontFamily: 'NSansL',
        fontSize: 16,
        color: appColors.white,
      ),
    );
  }

  Widget _buildMetaMaskButton(
    BuildContext context,
    MetaMaskProvider provider,
    Size size,
  ) {
    EdgeInsets dp = MediaQuery.of(context).padding;
    return Material(
      borderRadius: BorderRadius.circular(100),
      color: appColors.white,
      child: InkWell(
        onTap: provider.isConnecting ? null : () => provider.connect(),
        splashColor: Colors.black12,
        borderRadius: BorderRadius.circular(100),
        child: Container(
          height: 50,
          width: size.width - 24,
          padding: const EdgeInsets.symmetric(horizontal: 15),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              SvgPicture.asset('assets/images/metamask.svg', height: 25),
              Text(
                'Continue with MetaMask',
                style: TextStyle(
                  color: appColors.black,
                  fontSize: 16,
                  fontFamily: 'NSansM',
                ),
              ),
              const Icon(
                CupertinoIcons.arrow_right,
                color: Colors.black,
                size: 25,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildManualWalletField(
    BuildContext context,
    MetaMaskProvider provider,
    Size size,
  ) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 12),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          GeneratorTextfeild(
            hintText: 'Enter you public wallet address',
            textEditingController: _walletController,
            opacity: 0.08,
            hintOpacity: 0.25,
          ),
          const SizedBox(height: 12),
          Material(
            borderRadius: BorderRadius.all(Radius.circular(100)),
            color: appColors.white,
            child: InkWell(
              onTap: () {
                final address = _walletController.text.trim();
                if (address.isNotEmpty) {
                  provider.loginWithAddress(address);
                }
              },
              splashColor: Colors.black12,
              borderRadius: BorderRadius.circular(100),
              child: Container(
                height: 50,
                width: size.width - 24,
                padding: const EdgeInsets.symmetric(horizontal: 15),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Icon(
                      CupertinoIcons.arrow_right,
                      color: Colors.transparent,
                      size: 25,
                    ),
                    Text(
                      'Continue with Wallet Address',
                      style: TextStyle(
                        color: appColors.black,
                        fontSize: 16,
                        fontFamily: 'NSansM',
                      ),
                    ),
                    const Icon(
                      CupertinoIcons.arrow_right,
                      color: Colors.black,
                      size: 25,
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
