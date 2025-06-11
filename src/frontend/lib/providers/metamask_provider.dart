

import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:url_launcher/url_launcher_string.dart';
import 'package:walletconnect_flutter_v2/walletconnect_flutter_v2.dart';

class MetaMaskProvider extends ChangeNotifier {
  // --- STATE --- //
  Web3App? _web3app;
  SessionData? _session;
  String? _account;
  bool _isConnected = false;
  bool _onboardingComplete = false;
  bool _isConnecting = false;

  // --- GETTERS --- //
  String? get walletAddress => _account;
  bool get isConnected => _isConnected;
  bool get isOnboardingComplete => _onboardingComplete;
  bool get isConnecting => _isConnecting;

  // --- CONSTRUCTOR --- //
  MetaMaskProvider() {
    _init();
  }

  // --- INITIALIZATION --- //
  Future<void> _init() async {
    final prefs = await SharedPreferences.getInstance();

    _web3app = await Web3App.createInstance(
      projectId: '3b68b1320c7b316633e1aed418ef13f8',
      metadata: const PairingMetadata(
        name: 'Noodl',
        description: 'Learn anything and everything the smart way.',
        url: 'https://noodl.app',
        icons: ['https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/MetaMask_Fox.svg/2048px-MetaMask_Fox.svg.png'],
        redirect: Redirect(
            native: 'noodlapp://',
            universal: 'https://noodl.app'
        ),
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
        _onboardingComplete = prefs.getBool('onboardingComplete_${_account}') ?? false;
        notifyListeners();
      }
    }
  }

  // --- WALLETCONNECT EVENT HANDLERS --- //
  void _onSessionConnect(SessionConnect? args) async {
    _isConnecting = false;
    if (args != null) {
      final prefs = await SharedPreferences.getInstance();
      _session = args.session;
      _account = NamespaceUtils.getAccount(
        _session!.namespaces.values.first.accounts.first,
      );
      _isConnected = true;
      _onboardingComplete = prefs.getBool('onboardingComplete_${_account}') ?? false;
      notifyListeners();
    } else {
      notifyListeners();
    }
  }

  void _onSessionDelete(SessionDelete? args) {
    _clearSession();
  }

  // --- PUBLIC METHODS --- //
  Future<void> connect() async {
    if (_web3app == null) return;
    _isConnecting = true;
    notifyListeners();
    try {
      final ConnectResponse response = await _web3app!.connect(
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
      debugPrint('Error connecting: $e');
      _isConnecting = false;
      notifyListeners();
    }
  }

  // ‼️ UPDATED TO RETURN A BOOLEAN AND FIX THE ENDPOINT/PAYLOAD ‼️
  Future<bool> completeOnboarding(String name, String country) async {
    if (_account == null || _session == null) return false;

    // FIX 1: Use the correct endpoint URL. For local development with an
    // Android emulator, '10.0.2.2' points to the host machine's localhost.
    // For iOS simulator, you would use 'localhost' or '127.0.0.1'.
    final url = Uri.parse('http://1725364.xyz:5000/users');

    try {
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        // FIX 2: Send only the data the backend expects: wallet_address, name, country.
        body: json.encode({
          'wallet_address': _account,
          'name': name,
          'country': country,
        }),
      );

      // Check for a successful response from the server (201 Created)
      if (response.statusCode == 201) {
        final prefs = await SharedPreferences.getInstance();
        await prefs.setBool('onboardingComplete_${_account!}', true);
        _onboardingComplete = true;
        notifyListeners();
        return true; // <-- Return true on success
      } else {
        // Log the server error if the status code is not what we expect
        debugPrint('Server error: ${response.statusCode} - ${response.body}');
        return false; // <-- Return false on server error
      }
    } catch (e) {
      // Catch network errors (e.g., no internet, server down)
      debugPrint('Failed to send onboarding data: $e');
      return false; // <-- Return false on network error
    }
  }

  Future<void> disconnect() async {
    if (_session != null) {
      await _web3app!.disconnectSession(
        topic: _session!.topic,
        reason: const WalletConnectError(code: 1, message: 'User disconnected'),
      );
      _clearSession();
    }
  }

  // --- PRIVATE HELPERS --- //
  void _clearSession() async {
    final prefs = await SharedPreferences.getInstance();
    if (_account != null) {
      await prefs.remove('onboardingComplete_${_account!}');
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

