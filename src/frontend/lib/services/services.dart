import 'dart:convert';
import 'dart:math';

import 'package:frontend/models/core_level_model.dart';
import 'package:frontend/models/full_level_content_model.dart';
import 'package:frontend/models/noodl_model.dart';
import 'package:http/http.dart' as http;

class APIservice{

  static Future<dynamic> getLevel(int learningPathID, int level) async{
    Uri url = Uri.parse('http://1725364.xyz:5000/paths/$learningPathID/levels/$level');

    final response = await http.get(url);

    // print(response.statusCode);     
    return jsonDecode(response.body);
  }

  static Future<Map<String, dynamic>> generateNoodle({required String prompt, required String walletAdd}) async{
    Uri url = Uri.parse('http://1725364.xyz:5000/paths/generate');
    try{ 
      final response = await http.post(
        url,
        headers: {
          'Content-Type': 'application/json'
        },
        body: jsonEncode({
          "topic": prompt,
          "creator_wallet": walletAdd
        })
      );

      // print(response.statusCode);
      // print(response.body);
      return jsonDecode(response.body) ;

    } catch(e){
      print("ERROR: $e");
      return {
        "message": "E"
      };
    }
  }

  static Future<dynamic> generatingNoodlProgress({required String taskID}) async{
    Uri url = Uri.parse('http://1725364.xyz:5000/paths/generate/status/$taskID');
    final response = await http.get(
      url
    );
    // print("progress");
    // print(response.statusCode);
    // print(response.body);
    return jsonDecode(response.body);
  }

  static Future<dynamic> getCommunityNoodls() async{
    Uri url = Uri.parse('http://1725364.xyz:5000/paths');
    List<NoodlModel> results = [];
    try{
      final response = await http.get(url);
      dynamic data = jsonDecode(response.body);
      // print(data);
      for(var i in data){
        print(i);
        results.add(
          NoodlModel(
            createdAt: i['created_at'].toString(),
            description: i['short_description'] as String,
            id: i['id'],
            title: i['title'] as String,
            totalLevels: i['total_levels'] 
          )
        );
      }
      return results;
    } catch(e){
      print("Err community noodls: $e");
    }

  }


  static Future<dynamic> getUserNoodls({required String walletAdd, int limit=-1}) async{
    Uri url = Uri.parse('http://1725364.xyz:5000/users/$walletAdd/paths');
    List<NoodlModel> results = [];
    try{
      final response = await http.get(url);
      dynamic data = jsonDecode(response.body);
      for(var i in data){
        results.add(
          NoodlModel(
            createdAt: i['created_at'],
            description: i['short_description'],
            id: i['id'],
            title: i['title'],
            totalLevels: i['total_levels']
          )
        );
      }
      return limit<1?results:results.sublist(0, min(limit, results.length));
    } catch(e){
      print("Err user noodls: $e");
    }
  }


  static Future<CoreNoodleDataModel?> fetchLevelsFromNoodl({required int pathID}) async {
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
  
  static Future<LevelContentModel?> fetchLevelContent({required int pathID, required int levelID}) async {
    final Uri url = Uri.parse('http://1725364.xyz:5000/paths/$pathID/levels/$levelID');
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

  static Future<dynamic> fetchUserNameCountry({required String walletAdd}) async{
    final Uri url = Uri.parse('http://1725364.xyz:5000/users/$walletAdd');
    try{
      final response = await http.get(url);
      if(response.statusCode == 200 || response.statusCode==404){
        return jsonDecode(response.body);
      } else{
        print("ERR @ /users/<walletID>: ${response.statusCode}");
      }
    } catch(e){
        print("ERR @ /users/<walletID>: $e");
    }
    return null;
  }



}