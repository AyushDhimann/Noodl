import 'package:flutter/material.dart';

class QuizPageProvider extends ChangeNotifier{

  int totalQuestions = 0;

  void setTotalQuestions(int number){
    totalQuestions = number;
    notifyListeners();
  }

  int quizScore = 0;

  void increaseScore(){
    quizScore += 1;
    print('Score + 1 | Total = $quizScore');
    notifyListeners();
  }

  void zeroScore(){
    quizScore = 0;
    print('Score Reset');

    notifyListeners();
  }


  int selectedOption=0;

  void changeSelectedOption(int newOption){
    selectedOption = newOption;
    notifyListeners();
  }

  void setNoSelectedOption(){
    selectedOption = 0;
    notifyListeners();
  }


  int progress = 0;

  void setProgressBarZero(){
    progress = 0;
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