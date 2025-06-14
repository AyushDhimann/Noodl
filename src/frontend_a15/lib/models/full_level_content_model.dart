import 'package:frontend/models/quiz_item_model.dart';
import 'package:frontend/models/slide_item_model.dart';

class LevelContentModel {
  final String levelTitle;
  final int totalQuestionsInLevel;
  final int totalSlidesInLevel;
  final List<dynamic> items; // can be SlideItemModel or QuizItemModel

  LevelContentModel({
    required this.levelTitle,
    required this.totalQuestionsInLevel,
    required this.totalSlidesInLevel,
    required this.items,
  });

  factory LevelContentModel.fromJson(Map<String, dynamic> json) {
    final List<dynamic> parsedItems = json['items'].map((item) {
      if (item['item_type'] == 'quiz') {
        return QuizItemModel.fromJson(item);
      } else {
        return SlideItemModel.fromJson(item);
      }
    }).toList();

    return LevelContentModel(
      levelTitle: json['level_title'],
      totalQuestionsInLevel: json['total_questions_in_level'],
      totalSlidesInLevel: json['total_slides_in_level'],
      items: parsedItems,
    );
  }
}
