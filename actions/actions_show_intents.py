from typing import Text, List, Dict, Any
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


class ActionShowIntents(Action):
    def name(self) -> Text:
        return "action_show_intents"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.latest_message['intent'].get('name')
        return intent
        

# class ActionAskKnowledgeBaseSanPham(Action):

#     def name(self) -> Text:
#         return "action_custom_san_pham"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         text = tracker.latest_message['text']
#         text_input = text.lower()
#         sqlite_select_query = ''' SELECT * from san_pham'''
#         cursor.execute(sqlite_select_query)
#         record = cursor.fetchall()
#         san_pham_slot = tracker.get_slot("san_pham")
#         for index in record:
#             san_pham = result[0].lower()
#             loai_san_pham = result[1].lower()
#             gia = result[2].lower()
#             if san_pham in text_input:
#                 check = True
#                 dispatcher.utter_message("Nội dung bạn muốn bot trả lời")
#             elif san_pham_slot in text_input:
#                 check = True
#                 dispatcher.utter_message("Nội dung bạn muốn con bot trả lời")
#         if not check:
#             dispatcher.utter_message("Dạ cửa hàng em chưa có sản phẩm như anh chi cần ạ")