class HelperFunctions {
  static String markdownToPlainText(String input) {
    // Remove Markdown formatting
    String text = input
        .replaceAll(RegExp(r'!\[.*?\]\(.*?\)'), '') // Images
        .replaceAll(RegExp(r'\[([^\]]+)\]\([^)]+\)'), r'\1') // Links
        .replaceAll(RegExp(r'[*_~`>#]'), '') // *, _, ~, `, >, #
        .replaceAll(RegExp(r'\n{2,}'), '\n') // Reduce multiple newlines
        .replaceAll(RegExp(r'`{1,3}.*?`{1,3}'), '') // Inline code
        .replaceAll(RegExp(r'\*\*(.*?)\*\*'), r'\1') // Bold
        .replaceAll(RegExp(r'__(.*?)__'), r'\1'); // Bold with __

    // Replace - with space
    text = text.replaceAll('-', ' ');

    // Replace : with .
    text = text.replaceAll(':', '.');

    // Remove emojis (Unicode emoji range)
    text = text.replaceAll(RegExp(
      r'[\u{1F600}-\u{1F64F}' // Emoticons
      r'\u{1F300}-\u{1F5FF}' // Misc symbols and pictographs
      r'\u{1F680}-\u{1F6FF}' // Transport and map symbols
      r'\u{2600}-\u{26FF}'   // Misc symbols
      r'\u{2700}-\u{27BF}'   // Dingbats
      r'\u{1F1E6}-\u{1F1FF}]',
      unicode: true), '');

    // Remove special characters except space and basic punctuation
    text = text.replaceAll(RegExp(r'[^\w\s.,!?]'), '');

    return text.trim();
  }
}
