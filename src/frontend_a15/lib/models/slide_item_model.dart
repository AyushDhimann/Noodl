class SlideItemModel {
  final int id;
  final int itemIndex;
  final String itemType;
  final String content;

  SlideItemModel({
    required this.id,
    required this.itemIndex,
    required this.itemType,
    required this.content,
  });

  factory SlideItemModel.fromJson(Map<String, dynamic> json) {
    return SlideItemModel(
      id: json['id'],
      itemIndex: json['item_index'],
      itemType: json['item_type'],
      content: json['content'],
    );
  }
}
