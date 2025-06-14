import 'package:flutter/cupertino.dart';

class LoginPageProvider extends ChangeNotifier{
  PageController loginPageController = PageController();
  
  void goNextPage(){
    loginPageController.hasClients?
    loginPageController.animateToPage(1, duration: Duration(milliseconds: 250), curve: Curves.fastEaseInToSlowEaseOut):null;
  }
  void goPrevPage(){
    loginPageController.hasClients?
    loginPageController.animateToPage(0, duration: Duration(milliseconds: 250), curve: Curves.fastEaseInToSlowEaseOut):null;
  }

  bool loggingOut = false;

  void loggingOutTrue(){
    loggingOut = true;
    notifyListeners();

  }
  void loggingOutFalse(){
    loggingOut = false;
    notifyListeners();

  }

  
  @override
  void dispose() {
    loginPageController.dispose();
    super.dispose();
  }
}