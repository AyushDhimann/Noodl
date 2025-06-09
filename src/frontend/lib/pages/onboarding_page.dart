import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:frontend/constants/colors.dart' as appColors;
import 'package:frontend/providers/metamask_provider.dart';
import 'package:provider/provider.dart';

class OnboardingPage extends StatefulWidget {
  const OnboardingPage({super.key});

  @override
  State<OnboardingPage> createState() => _OnboardingPageState();
}

class _OnboardingPageState extends State<OnboardingPage> {
  final _nameController = TextEditingController();
  final _countryController = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  bool _isLoading = false;

  Future<void> _submit() async {
    // Check if the form is valid and not already loading
    if (_isLoading || !_formKey.currentState!.validate()) {
      return;
    }

    setState(() {
      _isLoading = true;
    });

    final provider = context.read<MetaMaskProvider>();
    final bool success = await provider.completeOnboarding(
      _nameController.text,
      _countryController.text,
    );

    // If the page is still mounted (i.e., we haven't navigated away)
    if (mounted) {
      // If the submission failed, stop loading and show an error
      if (!success) {
        setState(() {
          _isLoading = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Text('Failed to save profile. Please try again.'),
            backgroundColor: appColors.red,
          ),
        );
      }
      // If successful, the provider will notify listeners and the main app
      // router will automatically navigate to the HomePage. We don't need
      // to do anything else here.
    }
  }

  @override
  void dispose() {
    _nameController.dispose();
    _countryController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    Size size = MediaQuery.of(context).size;

    return Scaffold(
      backgroundColor: appColors.bgColor,
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24),
          child: Form(
            key: _formKey,
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '👋 One last step...',
                  style: TextStyle(
                      fontFamily: 'NSansB', fontSize: 28, color: appColors.white),
                ),
                const SizedBox(height: 8),
                Text(
                  'Please tell us a bit about yourself to complete your profile.',
                  style: TextStyle(
                      fontFamily: 'NSansL', fontSize: 18, color: appColors.white.withOpacity(0.8)),
                ),
                const SizedBox(height: 40),
                TextFormField(
                  controller: _nameController,
                  style: TextStyle(color: appColors.white, fontFamily: 'NSansM'),
                  decoration: _inputDecoration('Your Name'),
                  validator: (value) =>
                  value == null || value.isEmpty ? 'Please enter your name' : null,
                ),
                const SizedBox(height: 20),
                TextFormField(
                  controller: _countryController,
                  style: TextStyle(color: appColors.white, fontFamily: 'NSansM'),
                  decoration: _inputDecoration('Your Country'),
                  validator: (value) =>
                  value == null || value.isEmpty ? 'Please enter your country' : null,
                ),
                const SizedBox(height: 40),
                _isLoading
                    ? Center(child: CircularProgressIndicator(color: appColors.primary))
                    : Material(
                  borderRadius: const BorderRadius.all(Radius.circular(12.5)),
                  color: appColors.primary,
                  child: InkWell(
                    onTap: _submit,
                    borderRadius: const BorderRadius.all(Radius.circular(12.5)),
                    child: Container(
                      height: 50,
                      width: size.width - 48,
                      alignment: Alignment.center,
                      child: Text(
                        'Complete Profile & Continue',
                        style: TextStyle(
                            color: appColors.black, fontSize: 16, fontFamily: 'NSansB'),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  InputDecoration _inputDecoration(String label) {
    return InputDecoration(
      labelText: label,
      labelStyle: TextStyle(color: appColors.white.withOpacity(0.5)),
      filled: true,
      fillColor: appColors.grey,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12.5),
        borderSide: BorderSide.none,
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12.5),
        borderSide: BorderSide(color: appColors.primary, width: 2),
      ),
    );
  }
}