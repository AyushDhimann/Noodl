import 'package:flutter/material.dart';
import 'package:walletconnect_dart/walletconnect_dart.dart';
import 'package:url_launcher/url_launcher.dart';

class WalletConnector extends StatefulWidget {
  @override
  _WalletConnectorState createState() => _WalletConnectorState();
}

class _WalletConnectorState extends State<WalletConnector> {
  late WalletConnect connector;
  SessionStatus? _session;

  @override
  void initState() {
    super.initState();

    connector = WalletConnect(
      bridge: 'https://bridge.walletconnect.org',
      clientMeta: const PeerMeta(
        name: 'Noodl',
        description: 'Learn Finance with Web3',
        url: 'https://noodl.app',
        icons: ['https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/MetaMask_Fox.svg/2048px-MetaMask_Fox.svg.png'],
      ),
    );

    connector.on('connect', (session) => setState(() {
          _session = session as SessionStatus;
        }));

    connector.on('session_update', (payload) => print(payload));
    connector.on('disconnect', (payload) => setState(() {
          _session = null;
        }));
  }

  Future<void> connectWallet() async {
    if (!connector.connected) {
      try {
        final session = await connector.createSession(
          chainId: 1,
          onDisplayUri: (uri) async {
            await launchUrl(Uri.parse(uri), mode: LaunchMode.externalApplication);
          },
        );
        setState(() {
          _session = session;
        });
      } catch (e) {
        print(e);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final walletAddress = _session?.accounts.firstOrNull ?? "Not Connected";

    return Scaffold(
      appBar: AppBar(title: Text("Noodl - Connect Wallet")),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text("Wallet: $walletAddress"),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: connectWallet,
              child: const Text("Connect MetaMask"),
            ),
          ],
        ),
      ),
    );
  }
}
