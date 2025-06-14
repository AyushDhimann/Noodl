import 'package:flutter/material.dart';
import 'package:frontend/widgets/generate/logs_display.dart';

class GeneratePageProvider extends ChangeNotifier{
  String? generatingTaskID;
  bool? isGenerationComplete;
  bool initialLoading = false;

  void initialLoadingTrue(){
    initialLoading = true;
    notifyListeners();
  }

  void initialLoadingFalse(){
    initialLoading = false;
    notifyListeners();
  }

  void setGeneratingTaskID(String id){
    generatingTaskID = id;
    notifyListeners();
  }

  void nullGenereatingTaskID(){
    generatingTaskID = null;
    notifyListeners();
  }

  void setGeneratingBoolTrue(){
    isGenerationComplete = true;
    notifyListeners();
  }

  void setGeneratingBoolFalse(){
    isGenerationComplete = false;
    notifyListeners();
  }

  void nullifyGeneratingBool(){
    isGenerationComplete = null;
    notifyListeners();
  }

  ScrollController logsDisplayScrollController = ScrollController();

  void logsDisplayScrollToBottom(){

    logsDisplayScrollController.hasClients?
    logsDisplayScrollController.animateTo(
      logsDisplayScrollController.position.maxScrollExtent,
      duration: Duration(milliseconds: 100),
      curve: Curves.linear
    ):null;
  }

  TextEditingController generatorTextEditingController = TextEditingController();

  setATopicInGenerationFeild(String topic){
    generatorTextEditingController.text = topic;
    notifyListeners();
  }

  bool isRandomTopicLoading = false;

  void setRandomTopicLoadingTrue(){
    isRandomTopicLoading = true;
    notifyListeners();
  }
  void setRandomTopicLoadingFalse(){
    isRandomTopicLoading = false;
    notifyListeners();
  }

}