import 'package:flutter/material.dart';
import 'package:frontend/widgets/generate/logs_display.dart';

class GeneratePageProvider extends ChangeNotifier{
  String? generatingTaskID;
  bool? isGenerationComplete;

  setGeneratingTaskID(String id){
    generatingTaskID = id;
    notifyListeners();
  }

  nullGenereatingTaskID(){
    generatingTaskID = null;
    notifyListeners();
  }

  setGeneratingBoolTrue(){
    isGenerationComplete = true;
    notifyListeners();
  }

  setGeneratingBoolFalse(){
    isGenerationComplete = false;
    notifyListeners();
  }

  nullifyGeneratingBool(){
    isGenerationComplete = null;
    notifyListeners();
  }

  ScrollController logsDisplayScrollController = ScrollController();

  logsDisplayScrollToBottom(){

    logsDisplayScrollController.hasClients?
    logsDisplayScrollController.animateTo(
      logsDisplayScrollController.position.maxScrollExtent,
      duration: Duration(milliseconds: 100),
      curve: Curves.linear
    ):null;
  }

  TextEditingController generatorTextEditingController = TextEditingController();
}