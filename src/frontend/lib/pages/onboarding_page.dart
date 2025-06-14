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
            content: Text(
              'Failed to save profile. Please try again.',
              style: TextStyle(
                fontSize: 14, 
                fontFamily: 'NSansM',
                color: appColors.white
              ),
            ),
            backgroundColor: appColors.grey,
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
    EdgeInsets dp = MediaQuery.of(context).padding;

    return GestureDetector(
      onTap: () => FocusScope.of(context).unfocus(),
      child: Scaffold(
        backgroundColor: appColors.bgColor,
        body: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 12),
          child: Form(
            key: _formKey,
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                SizedBox(height: dp.top+12,),
                Text(
                  'One More Thing...',
                  style: TextStyle(
                    fontFamily: 'NSansB',
                    fontSize: 22,
                    color: appColors.white,
                  ),
                ),
                SizedBox(height: 12,),
                Container(
                  width: size.width-24,
                  height: (size.width-24)*0.5583,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.all(Radius.circular(12.5)),
                    image: DecorationImage(
                      image: AssetImage('assets/images/one_more_thing.gif')
                    )
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  'Please tell us a bit about yourself to complete your profile.',
                  style: TextStyle(
                    fontFamily: 'NSansL',
                    fontSize: 16,
                    color: appColors.white.withOpacity(0.8),
                  ),
                ),
                const SizedBox(height: 12),
                Container(
                  padding: EdgeInsets.symmetric(horizontal: 12),
                  decoration: BoxDecoration(
                    color: appColors.white.withOpacity(0.08),
                    borderRadius: BorderRadius.all(Radius.circular(10)),
                  ),
                  child: TextFormField(
                    controller: _nameController,
                    style: TextStyle(
                      color: appColors.white,
                      fontFamily: 'NSansM',
                    ),
                    decoration: _inputDecoration('Your Name'),
                    validator: (value) => value == null || value.isEmpty
                        ? 'Please enter your name'
                        : null,
                  ),
                ),
                const SizedBox(height: 12),
                Container(
                  padding: EdgeInsets.symmetric(horizontal: 12),
                  decoration: BoxDecoration(
                    color: appColors.white.withOpacity(0.08),
                    borderRadius: BorderRadius.all(Radius.circular(10)),
                  ),
                  child: TextFormField(
                    controller: _countryController,
                    style: TextStyle(
                      color: appColors.white,
                      fontFamily: 'NSansM',
                    ),
                    decoration: _inputDecoration('Your Country'),
                    validator: (value) => value == null || value.isEmpty
                        ? 'Please enter your country'
                        : null,
                  ),
                ),
                const SizedBox(height: 24),
                _isLoading
                    ? Center(
                        child: CircularProgressIndicator(
                          color: appColors.primary,
                        ),
                      )
                    : Material(
                        borderRadius: const BorderRadius.all(
                          Radius.circular(100),
                        ),
                        color: appColors.primary,
                        child: InkWell(
                          onTap: _submit,
                          borderRadius: const BorderRadius.all(
                            Radius.circular(100),
                          ),
                          child: Container(
                            height: 50,
                            width: size.width - 24,
                            alignment: Alignment.center,
                            child: Text(
                              'Complete Profile & Continue',
                              style: TextStyle(
                                color: appColors.black,
                                fontSize: 16,
                                fontFamily: 'NSansM',
                              ),
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
      border: InputBorder.none,

      hintText: label,
      hintStyle: TextStyle(
        color: appColors.white.withOpacity(0.25),
        fontFamily: 'NSansL',
      ),
    );
  }
}
