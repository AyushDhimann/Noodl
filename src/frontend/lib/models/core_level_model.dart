class CoreNoodleDataModel {
  final String title;
  final String titleEmbedding;
  final int totalLevels;
  final int totalQuestions;
  final int totalSlides;
  final String contentHash;
  final String createdAt;
  final String creatorWallet;
  final String longDescription;
  final int id;
  final List<MiniLevelModel> levels;

  CoreNoodleDataModel({
    required this.title,
    required this.titleEmbedding,
    required this.totalLevels,
    required this.totalQuestions,
    required this.totalSlides,
    required this.contentHash,
    required this.createdAt,
    required this.creatorWallet,
    required this.longDescription,
    required this.id,
    required this.levels,
  });

  factory CoreNoodleDataModel.fromJson(Map<String, dynamic> json) {
    return CoreNoodleDataModel(
      title: json['title'],
      titleEmbedding: json['title_embedding'],
      totalLevels: json['total_levels'],
      totalQuestions: json['total_questions'],
      totalSlides: json['total_slides'],
      contentHash: json['content_hash'],
      createdAt: json['created_at'],
      creatorWallet: json['creator_wallet'],
      longDescription: json['long_description'].toString(),
      id: json['id'],
      levels: (json['levels'] as List)
          .map((levelJson) => MiniLevelModel.fromJson(levelJson))
          .toList(),
    );
  }
}

class MiniLevelModel {
  final String createdAt;
  final int id;
  final int levelNumber;
  final String levelTitle;
  final int pathId;

  MiniLevelModel({
    required this.createdAt,
    required this.id,
    required this.levelNumber,
    required this.levelTitle,
    required this.pathId,
  });

  factory MiniLevelModel.fromJson(Map<String, dynamic> json) {
    return MiniLevelModel(
      createdAt: json['created_at'],
      id: json['id'],
      levelNumber: json['level_number'],
      levelTitle: json['level_title'],
      pathId: json['path_id'],
    );
  }
}
