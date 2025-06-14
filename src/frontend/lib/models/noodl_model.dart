class NoodlModel {
  final String createdAt;
  final String description; // short desc
  final int id;
  final String title;
  final int totalLevels;
  final bool? isComplete;

  NoodlModel({
    required this.createdAt,
    required this.description,
    required this.id,
    required this.title,
    required this.totalLevels,
    this.isComplete

  });
}