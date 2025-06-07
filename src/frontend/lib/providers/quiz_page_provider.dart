import 'package:flutter/material.dart';

class QuizPageProvider extends ChangeNotifier{
  int selectedOption=0;

  void changeSelectedOption(int newOption){
    selectedOption = newOption;
    notifyListeners();
  }

}