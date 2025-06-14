import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:url_launcher/url_launcher_string.dart';
import 'package:walletconnect_flutter_v2/walletconnect_flutter_v2.dart';

class MetaMaskProvider extends ChangeNotifier {
  Web3App? _web3app;
  SessionData? _session;
  String? _account;
  bool _isConnected = false;
  bool _onboardingComplete = false;
  bool _isConnecting = false;

  // Getters
  String? get walletAddress => _account;
  bool get isConnected => _isConnected;
  bool get isOnboardingComplete => _onboardingComplete;
  bool get isConnecting => _isConnecting;

  MetaMaskProvider() {
    _init();
  }

  Future<void> _init() async {
    final prefs = await SharedPreferences.getInstance();

    final savedAddress = prefs.getString('wallet_address');
    if (savedAddress != null && savedAddress.isNotEmpty) {
      _account = savedAddress;
      _isConnected = true;
      _onboardingComplete =
          prefs.getBool('onboardingComplete_$savedAddress') ?? false;
      notifyListeners();
    }

    _web3app = await Web3App.createInstance(
      projectId: '3b68b1320c7b316633e1aed418ef13f8',
      metadata: const PairingMetadata(
        name: 'Noodl',
        description: 'Learn anything and everything the smart way.',
        url: 'https://noodl.app',
        icons: [
          'https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/MetaMask_Fox.svg/2048px-MetaMask_Fox.svg.png'
        ],
        redirect: Redirect(native: 'noodlapp://', universal: 'https://noodl.app'),
      ),
    );

    _web3app!.onSessionConnect.subscribe(_onSessionConnect);
    _web3app!.onSessionDelete.subscribe(_onSessionDelete);

    if (_web3app!.sessions.getAll().isNotEmpty) {
      _session = _web3app!.sessions.getAll().first;
      if (_session != null) {
        _account = NamespaceUtils.getAccount(
          _session!.namespaces.values.first.accounts.first,
        );
        _isConnected = true;
        _onboardingComplete =
            prefs.getBool('onboardingComplete_$_account') ?? false;
        await prefs.setString('wallet_address', _account!);
        notifyListeners();
      }
    }
  }

  void _onSessionConnect(SessionConnect? args) async {
    _isConnecting = false;
    if (args != null) {
      final prefs = await SharedPreferences.getInstance();
      _session = args.session;
      _account = NamespaceUtils.getAccount(
        _session!.namespaces.values.first.accounts.first,
      );
      _isConnected = true;
      _onboardingComplete =
          prefs.getBool('onboardingComplete_$_account') ?? false;
      await prefs.setString('wallet_address', _account!);
      notifyListeners();
    }
  }

  void _onSessionDelete(SessionDelete? args) {
    _clearSession();
  }

  Future<void> connect() async {
    if (_web3app == null) return;
    _isConnecting = true;
    notifyListeners();

    try {
      final response = await _web3app!.connect(
        requiredNamespaces: {
          'eip155': const RequiredNamespace(
            chains: ['eip155:1'],
            methods: ['personal_sign'],
            events: ['chainChanged', 'accountsChanged'],
          ),
        },
      );
      await launchUrlString(response.uri.toString(), mode: LaunchMode.externalApplication);
    } catch (e) {
      debugPrint('WalletConnect Error: $e');
      _isConnecting = false;
      notifyListeners();
    }
  }

  /// Manual login without WalletConnect
  Future<void> loginWithAddress(String walletAddress) async {
    final prefs = await SharedPreferences.getInstance();
    _account = walletAddress;
    _isConnected = true;
    _onboardingComplete =
        prefs.getBool('onboardingComplete_$walletAddress') ?? false;
    await prefs.setString('wallet_address', walletAddress);
    notifyListeners();
  }

  /// Logout for both WalletConnect + manual login
  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();

    // Disconnect WalletConnect session if exists
    if (_session != null && _web3app != null) {
      try {
        await _web3app!.disconnectSession(
          topic: _session!.topic,
          reason: const WalletConnectError(
            code: 1,
            message: 'User disconnected',
          ),
        );
      } catch (e) {
        debugPrint('Disconnect error (safe to ignore if manual login): $e');
      }
    }

    if (_account != null) {
      await prefs.remove('wallet_address');
      await prefs.remove('onboardingComplete_$_account');
    }

    _session = null;
    _account = null;
    _isConnected = false;
    _isConnecting = false;
    _onboardingComplete = false;
    notifyListeners();
  }

  /// Onboarding API call
  Future<bool> completeOnboarding(String name, String country) async {
    if (_account == null) return false;

    final url = Uri.parse('http://1725364.xyz:5000/users');

    try {
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'wallet_address': _account,
          'name': name,
          'country': country,
        }),
      );

      if (response.statusCode == 201) {
        final prefs = await SharedPreferences.getInstance();
        await prefs.setBool('onboardingComplete_$_account', true);
        _onboardingComplete = true;
        notifyListeners();
        return true;
      } else {
        debugPrint('Server error: ${response.statusCode} - ${response.body}');
        return false;
      }
    } catch (e) {
      debugPrint('Onboarding error: $e');
      return false;
    }
  }

  Future<void> _clearSession() async {
    final prefs = await SharedPreferences.getInstance();
    if (_account != null) {
      await prefs.remove('wallet_address');
      await prefs.remove('onboardingComplete_$_account');
    }

    _session = null;
    _account = null;
    _isConnected = false;
    _onboardingComplete = false;
    _isConnecting = false;
    notifyListeners();
  }

  @override
  void dispose() {
    _web3app?.onSessionConnect.unsubscribe(_onSessionConnect);
    _web3app?.onSessionDelete.unsubscribe(_onSessionDelete);
    super.dispose();
  }
}
