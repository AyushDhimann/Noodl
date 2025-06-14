class QuizItemModel {
  final int id;
  final int itemIndex;
  final String itemType;
  final String question;
  final List<String> options;
  final int correctAnswerIndex;
  final String explanation;

  QuizItemModel({
    required this.id,
    required this.itemIndex,
    required this.itemType,
    required this.question,
    required this.options,
    required this.correctAnswerIndex,
    required this.explanation,
  });

  factory QuizItemModel.fromJson(Map<String, dynamic> json) {
    final content = json['content'];
    return QuizItemModel(
      id: json['id'],
      itemIndex: json['item_index'],
      itemType: json['item_type'],
      question: content['question'],
      options: List<String>.from(content['options']),
      correctAnswerIndex: content['correctAnswerIndex'],
      explanation: content['explanation'],
    );
  }
}
