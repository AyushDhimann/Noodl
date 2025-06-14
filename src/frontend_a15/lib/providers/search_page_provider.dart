import 'package:flutter/material.dart';
import 'package:frontend/models/search_result_model.dart';
import 'package:frontend/services/services.dart';

class SearchPageProvider with ChangeNotifier {
  final TextEditingController searchTextEditingController = TextEditingController();
  List<SearchPathResultModel> results = [];
  bool isLoading = false;

  SearchPageProvider() {
    searchTextEditingController.addListener(_onSearchChanged);
  }

  void _onSearchChanged() {
    final query = searchTextEditingController.text;
    if (query.length >= 2) {
      searchPaths(query);
    } else {
      results = [];
      notifyListeners();
    }
  }

  Future<void> searchPaths(String query) async {
    isLoading = true;
    notifyListeners();

    try {
      results = await APIservice.searchPaths(query);
    } catch (_) {
      results = [];
    }

    isLoading = false;
    notifyListeners();
  }

  @override
  void dispose() {
    searchTextEditingController.dispose();
    super.dispose();
  }
}
