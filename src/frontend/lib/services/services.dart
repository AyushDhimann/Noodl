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
}