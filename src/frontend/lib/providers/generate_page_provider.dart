import 'package:flutter/material.dart';
import 'package:frontend/widgets/generate/logs_display.dart';

class GeneratePageProvider extends ChangeNotifier{
  String? generatingTaskID;

  setGeneratingTaskID(String id){
    generatingTaskID = id;
    notifyListeners();
  }

  nullGenereatingTaskID(){
    generatingTaskID = null;
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
}