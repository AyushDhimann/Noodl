import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:frontend/constants/colors.dart' as appColors;
import 'package:frontend/providers/metamask_provider.dart';
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
    final size = MediaQuery.of(context).size;
    final dp = MediaQuery.of(context).padding;

    if (metaMaskProvider.isConnecting) {
      return _buildLoadingScreen(context);
    }

    return Scaffold(
      backgroundColor: appColors.bgColor,
      body: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SizedBox(height: dp.top + 24),
            Center(
              child: SvgPicture.asset(
                'assets/images/noodl.svg',
                width: size.width / 3,
              ),
            ),
            const SizedBox(height: 36),
            Expanded(
              child: SingleChildScrollView(
                physics: const BouncingScrollPhysics(),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildSectionTitle('🍜 Welcome to noodl.'),
                    _buildSectionText(
                      'Learn anything and everything the smart way — through short bursts, fun quizzes, and real rewards.',
                    ),
                    const SizedBox(height: 20),
                    _buildSectionTitle('🧠 Powered by Web3'),
                    _buildSectionText(
                      'Noodl uses secure blockchain technology to give you true ownership of your progress, achievements, and rewards.',
                    ),
                    const SizedBox(height: 20),
                    _buildSectionTitle('🦊 Sign in with MetaMask'),
                    _buildSectionText(
                      'We use MetaMask — a trusted Web3 wallet that lets you sign in without passwords.\n🎯 No emails. No third parties. Just you and your wallet.',
                    ),
                    const SizedBox(height: 24),
                    _buildMetaMaskButton(context, metaMaskProvider, size),
                    const SizedBox(height: 28),
                    _buildSectionTitle('✍️ Or enter your Wallet Address'),
                    const SizedBox(height: 10),
                    _buildManualWalletField(context, metaMaskProvider, size),
                  ],
                ),
              ),
            ),
            SizedBox(height: dp.bottom + 12),
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
        fontSize: 22,
        color: appColors.white,
      ),
    );
  }

  Widget _buildSectionText(String text) {
    return Text(
      text,
      style: TextStyle(
        fontFamily: 'NSansL',
        fontSize: 18,
        color: appColors.white,
      ),
    );
  }

  Widget _buildMetaMaskButton(BuildContext context, MetaMaskProvider provider, Size size) {
    return Center(
      child: Material(
        borderRadius: BorderRadius.circular(12.5),
        color: appColors.white,
        child: InkWell(
          onTap: provider.isConnecting ? null : () => provider.connect(),
          splashColor: Colors.black12,
          borderRadius: BorderRadius.circular(12.5),
          child: Container(
            height: 50,
            width: size.width - 24,
            padding: const EdgeInsets.symmetric(horizontal: 12),
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
                const Icon(CupertinoIcons.arrow_right, color: Colors.black, size: 25),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildManualWalletField(BuildContext context, MetaMaskProvider provider, Size size) {
    return Column(
      children: [
        TextField(
          controller: _walletController,
          style: TextStyle(color: appColors.white, fontFamily: 'NSansL'),
          decoration: InputDecoration(
            filled: true,
            fillColor: Colors.white10,
            hintText: 'Enter your public wallet address',
            hintStyle: TextStyle(color: appColors.white.withOpacity(0.5)),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12.5),
              borderSide: BorderSide.none,
            ),
            contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
          ),
        ),
        const SizedBox(height: 12),
        ElevatedButton.icon(
          onPressed: () {
            final address = _walletController.text.trim();
            if (address.isNotEmpty) {
              provider.loginWithAddress(address);
            }
          },
          icon: const Icon(CupertinoIcons.arrow_right, size: 20),
          label: const Text('Continue with Wallet Address'),
          style: ElevatedButton.styleFrom(
            foregroundColor: appColors.black,
            backgroundColor: appColors.white,
            minimumSize: Size(size.width - 24, 50),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12.5),
            ),
            textStyle: const TextStyle(fontSize: 16, fontFamily: 'NSansM'),
          ),
        ),
      ],
    );
  }
}
