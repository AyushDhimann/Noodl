// ignore_for_file: non_constant_identifier_names

class LearningPathModel{
  final String description;
  final int id;
  final String title;
  final int total_levels;

  LearningPathModel({
    required this.description,
    required this.id,
    required this.title,
    required this.total_levels
  });
  
}

class QuizSlideModel{
  final String content;
  final int id;
  final int item_index;
  final String item_type;

  QuizSlideModel({
    required this.content,
    required this.id,
    required this.item_index,
    required this.item_type
  });
  
}

class QuizQNASubmodel{
  final String question;
  final List<String> options;
  final int correct_index;
  final String explaination;

  QuizQNASubmodel({
    required this.question,
    required this.options,
    required this.correct_index,
    required this.explaination
  });

}

class QuizQNAMainModel{
  final QuizQNASubmodel content;
  final int id;
  final int item_index;
  final String item_type;

  QuizQNAMainModel({
    required this.content,
    required this.id,
    required this.item_index,
    required this.item_type
  });
  
}

