// ignore_for_file: avoid_print

import 'dart:convert';
import 'dart:math';

import 'package:frontend/models/core_level_model.dart';
import 'package:frontend/models/full_level_content_model.dart';
import 'package:frontend/models/noodl_model.dart';
import 'package:frontend/models/search_result_model.dart';
import 'package:frontend/models/user_nft_model.dart';
import 'package:http/http.dart' as http;

class APIservice {
  static Future<dynamic> getLevel(int learningPathID, int level) async {
    Uri url = Uri.parse(
      'http://1725364.xyz:5000/paths/$learningPathID/levels/$level',
    );

    final response = await http.get(url);

    // print(response.statusCode);
    return jsonDecode(response.body);
  }

  static Future<Map<String, dynamic>> generateNoodle({
    required String prompt,
    required String walletAdd,
  }) async {
    Uri url = Uri.parse('http://1725364.xyz:5000/paths/generate');
    try {
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({"topic": prompt, "creator_wallet": walletAdd}),
      );

      // print(response.statusCode);
      // print(response.body);
      return jsonDecode(response.body);
    } catch (e) {
      print("ERROR: $e");
      return {"message": "E"};
    }
  }

  static Future<dynamic> generatingNoodlProgress({
    required String taskID,
  }) async {
    Uri url = Uri.parse(
      'http://1725364.xyz:5000/paths/generate/status/$taskID',
    );
    final response = await http.get(url);
    // print("progress");
    // print(response.statusCode);
    // print(response.body);
    return jsonDecode(response.body);
  }

  static Future<dynamic> getCommunityNoodls() async {
    Uri url = Uri.parse('http://1725364.xyz:5000/paths');
    List<NoodlModel> results = [];
    try {
      final response = await http.get(url);
      dynamic data = jsonDecode(response.body);
      // print(data);
      for (var i in data) {
        print(i);
        results.add(
          NoodlModel(
            createdAt: i['created_at'].toString(),
            description: i['short_description'] as String,
            id: i['id'],
            title: i['title'] as String,
            totalLevels: i['total_levels'],
          ),
        );
      }
      return results;
    } catch (e) {
      print("Err community noodls: $e");
    }
  }

  static Future<dynamic> getUserNoodls({
    required String walletAdd,
    int limit = -1,
  }) async {
    Uri url = Uri.parse('http://1725364.xyz:5000/users/$walletAdd/paths');
    List<NoodlModel> results = [];
    try {
      final response = await http.get(url);
      dynamic data = jsonDecode(response.body);
      for (var i in data) {
        results.add(
          NoodlModel(
            createdAt: i['created_at'],
            description: i['short_description'],
            id: i['id'],
            title: i['title'],
            totalLevels: i['total_levels'],
            isComplete: i['is_complete'],
          ),
        );
      }
      return limit < 1
          ? results
          : results.sublist(0, min(limit, results.length));
    } catch (e) {
      print("Err user noodls: $e");
    }
  }

  static Future<CoreNoodleDataModel?> fetchLevelsFromNoodl({
    required int pathID,
  }) async {
    Uri url = Uri.parse('http://1725364.xyz:5000/paths/$pathID');
    try {
      final response = await http.get(url);

      if (response.statusCode == 200) {
        final json = jsonDecode(response.body);
        return CoreNoodleDataModel.fromJson(json);
      } else {
        print("Error: ${response.statusCode}");
      }
    } catch (e) {
      print("Exception caught: $e");
    }

    return null;
  }

  static Future<LevelContentModel?> fetchLevelContent({
    required int pathID,
    required int levelID,
  }) async {
    final Uri url = Uri.parse(
      'http://1725364.xyz:5000/paths/$pathID/levels/$levelID',
    );
    try {
      final response = await http.get(url);

      if (response.statusCode == 200) {
        final json = jsonDecode(response.body);
        return LevelContentModel.fromJson(json);
      } else {
        print("Error: ${response.statusCode}");
      }
    } catch (e) {
      print("Exception caught: $e");
    }

    return null;
  }

  static Future<dynamic> fetchUserNameCountry({
    required String walletAdd,
  }) async {
    final Uri url = Uri.parse('http://1725364.xyz:5000/users/$walletAdd');
    try {
      final response = await http.get(url);
      if (response.statusCode == 200 || response.statusCode == 404) {
        return jsonDecode(response.body);
      } else {
        print("ERR @ /users/<walletID>: ${response.statusCode}");
      }
    } catch (e) {
      print("ERR @ /users/<walletID>: $e");
    }
    return null;
  }

  // do this when when usr clicks on a lesson, theres not need for level i
  // learning path ID

  static Future<dynamic> sendUserScore({
    required String walletAdd,
    required int pathID,
    required int levelIndex,
    required int correctAnswers,
    required int totalQuestions,
  }) async {
    final Uri url = Uri.parse('http://1725364.xyz:5000/progress/level');
    try {
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          "user_wallet": walletAdd,
          "path_id": pathID,
          "level_index": levelIndex,
          "correct_answers": correctAnswers,
          "total_questions": totalQuestions,
        }),
      );
      print("POST /progress/level");
      print(
        "SENDING SCORE: LEVEL$levelIndex | C:$correctAnswers | T:$totalQuestions",
      );

      print(response.statusCode);
      print(response.body);
    } catch (e) {
      print("ERR @ START USER SCORES: $e");
    }
  }

  static Future<dynamic> mintNFT({
    required int pathID,
    required String walletAdd,
  }) async {
    final Uri url = Uri.parse('http://1725364.xyz:5000/paths/$pathID/complete');
    try {
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({"user_wallet": walletAdd}),
      );

      print("POST MINT NFT /paths/<pathid>/complete");

      print(response.statusCode);
      print(response.body);
      return jsonDecode(response.body);
    } catch (e) {
      print("ERR @  MINT NFT: $e");
    }
  }

  static Future<List<UserNftModel>> fetchUserNFTs({
    required String walletAdd,
  }) async {
    final Uri url = Uri.parse('http://1725364.xyz:5000/nfts/$walletAdd');
    List<UserNftModel> results = [];
    try {
      final response = await http.get(url);
      if (response.statusCode == 200) {
        dynamic data = jsonDecode(response.body);
        for (var i in data) {
          print(i['metadata_url']);
          results.add(
            UserNftModel(
              learningPathTitle: i['learning_paths']['title'].toString(),
              metaDataURL: i['metadata_url'].toString(),
              nftContractAdd: i['nft_contract_address'].toString(),
              networkImageURL: i['image_gateway_url'],
              mintedAt: i['minted_at'].toString(),
              pathID: i['path_id'],
              tokenID: i['token_id'],
            ),
          );
        }
      }
    } catch (e) {
      print("ERR @ FETCH USER NFTs: $e");
    }
    return results;
  }

  // add 1 to check if a user path is complete
  static Future<bool> isNoodlComplete({
    required String walletAdd,
    required int pathID,
  }) async {
    final Uri url = Uri.parse(
      'http://1725364.xyz:5000/progress/path/$pathID/$walletAdd/completed',
    );
    try {
      final response = await http.get(url);
      if (response.statusCode == 200) {
        return jsonDecode(response.body)['is_complete'];
      }
    } catch (e) {
      print('ERR @ isNoodlComp: $e');
    }
    return false;
  }

  //  is level complete

  static Future<List<SearchPathResultModel>> searchPaths(String query) async {
    if (query.length < 2) return [];

    final uri = Uri.parse(
      'http://1725364.xyz:5000/search?q=${Uri.encodeComponent(query)}',
    );
    final res = await http.get(uri);

    if (res.statusCode == 200) {
      final List data = json.decode(res.body);
      return data.map((item) => SearchPathResultModel.fromJson(item)).toList();
    } else {
      throw Exception('Failed to search paths');
    }
  }

  //  is level complete
  static Future<String?> fetchRandomTopic() async {
    try {
      final response = await http.get(
        Uri.parse('http://1725364.xyz:5000/paths/random-topic'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final jsonData = jsonDecode(response.body);
        return jsonData['topic'] as String?;
      } else {
        print('Failed to fetch random topic. Status: ${response.statusCode}');
        return null;
      }
    } catch (e) {
      print('Error fetching random topic: $e');
      return null;
    }
  }
}
