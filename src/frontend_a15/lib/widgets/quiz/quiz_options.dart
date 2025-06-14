import 'package:flutter/material.dart';
import 'package:frontend/models/quiz_item_model.dart';
import 'package:frontend/providers/quiz_page_provider.dart';
import 'package:frontend/widgets/quiz/quiz_answer_item.dart';
import 'package:provider/provider.dart';

class QuizOptions extends StatelessWidget {
  final QuizItemModel data;
  const QuizOptions({super.key, required this.data});

  @override
  Widget build(BuildContext context) {
    return Consumer<QuizPageProvider>(
      builder: (context, provider, child) => 
      Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          ...data.options.asMap().entries.map(
            (entry)=>QuizAnswerItem(
              selected: provider.selectedOption==entry.key+1,
              text: entry.value,
              uid: entry.key+1,
              onTap: ()=> provider.changeSelectedOption(entry.key+1)
              )
            ),
          
          
          // QuizAnswerItem(onTap: ()=>provider.changeSelectedOption(1),uid: 1,selected: provider.selectedOption==1, text: 'Universal Payment Integration',),
          // QuizAnswerItem(onTap: ()=>provider.changeSelectedOption(2),uid: 2,selected: provider.selectedOption==2, text: 'Unified Payment Interface',),
          // QuizAnswerItem(onTap: ()=>provider.changeSelectedOption(3),uid: 3,selected: provider.selectedOption==3, text: 'Unique Payment Identifier',),
          // QuizAnswerItem(onTap: ()=>provider.changeSelectedOption(4),uid: 4,selected: provider.selectedOption==4, text: 'Unified Processing Infrastructure',),
        ],
      ),
    );
  }
}

