import 'dart:convert';

import 'package:http/http.dart' as http;

class APIservice{

  static Future<dynamic> getPaths() async{
    Uri url = Uri.parse('http://1725364.xyz:5000/paths');

    final response = await http.get(url);

    print(response.statusCode);
    print(response.body);
    return jsonDecode(response.body);
  }

  static Future<dynamic> getLevel(int learningPathID, int level) async{
    Uri url = Uri.parse('http://1725364.xyz:5000/paths/$learningPathID/levels/$level');

    final response = await http.get(url);

    print(response.statusCode);
    print(response.body);
    return jsonDecode(response.body);
  }

  static Future<Map<String, dynamic>> generateNoodle({required String prompt, required String user_wallet_id}) async{
    Uri url = Uri.parse('http://1725364.xyz:5000/paths/generate');
    try{ 
      final response = await http.post(
        url,
        headers: {
          'Content-Type': 'application/json'
        },
        body: jsonEncode({
          "topic": prompt,
          "creator_wallet": '0x$user_wallet_id'
        })
      );

      print(response.statusCode);
      print(response.body);
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
    print("progress");
    print(response.statusCode);
    print(response.body);
    return jsonDecode(response.body);
  }
}