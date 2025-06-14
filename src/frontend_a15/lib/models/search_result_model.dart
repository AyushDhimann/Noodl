class SearchPathResultModel {
  final int id;
  final String matchType;
  final String title;
  final double? similarity;

  SearchPathResultModel({
    required this.id,
    required this.matchType,
    required this.title,
    this.similarity,
  });

  factory SearchPathResultModel.fromJson(Map<String, dynamic> json) {
    return SearchPathResultModel(
      id: json['id'],
      matchType: json['match_type'],
      title: json['title'],
      similarity: json['similarity']?.toDouble(),
    );
  }
}
