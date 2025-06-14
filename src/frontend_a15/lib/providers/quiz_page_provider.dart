import 'package:flutter/material.dart';

class QuizPageProvider extends ChangeNotifier{

  int totalItemsInLesson = 0;

  void setTotalQuestions(int number){
    totalItemsInLesson = number;
    notifyListeners();
  }

  int correctAnswers = 0;

  void increaseScore(){
    correctAnswers += 1;
    print('Score + 1 | Total = $correctAnswers');
    notifyListeners();
  }

  void zeroScore(){
    correctAnswers = 0;
    print('Score Reset');

    notifyListeners();
  }

  int questionCount = 0;

  void increaseQuestionCount(){
    questionCount += 1;
    notifyListeners();
  }

  void zeroQuestionCount(){
    questionCount = 0;
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