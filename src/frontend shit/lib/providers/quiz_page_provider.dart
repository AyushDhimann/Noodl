import 'package:flutter/material.dart';

class QuizPageProvider extends ChangeNotifier{
  int selectedOption=0;
  int progress = 0;
  void changeSelectedOption(int newOption){
    selectedOption = newOption;
    notifyListeners();
  }

  PageController quizQuesContoller = PageController();

  void goToNextQues(){
    quizQuesContoller.nextPage(
      duration: const Duration(milliseconds: 500),
      curve: Curves.linearToEaseOut
    );
    progress += 1;
    selectedOption = 0;
    notifyListeners();
  }

}