class UserNftModel {
  final String learningPathTitle;
  final String metaDataURL;
  final String networkImageURL;
  final String nftContractAdd;
  final String mintedAt;
  final int pathID;
  final int tokenID;

  UserNftModel({
    required this.learningPathTitle,
    required this.metaDataURL,
    required this.nftContractAdd,
    required this.networkImageURL,
    required this.mintedAt,
    required this.pathID,
    required this.tokenID,
  });
}
