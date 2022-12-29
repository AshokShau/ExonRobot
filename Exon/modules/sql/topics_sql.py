"""
  import threading

 from Exon.modules.sql import BASE, SESSION
 from sqlalchemy import Column, String, distinct, func


 class TopicsAction(BASE):
     __tablename__ = "topic_actions"
     chat_id = Column(String(14), primary_key=True)
     action_topic = Column(String(14))

     def __init__(self, chat_id):
         self.chat_id = chat_id

     def __repr__(self):
         return "<Chat {} action_topic: {}>".format(self.chat_id, self.action_topic)


 TopicsAction.__table__.create(checkfirst=True)

 INSERTION_LOCK = threading.RLock()


 def set_action_topic(chat_id: int, action_chat: int) -> int:
     with INSERTION_LOCK:
         action_topic = SESSION.query(TopicsAction).get(str(chat_id))
         if not action_topic:
             action_topic = TopicsAction(str(chat_id))
         action_topic.action_topic = action_chat

         SESSION.add(action_topic)
         SESSION.commit()


 def get_action_topic(chat_id: int) -> int | None:
     action_topic = SESSION.query(TopicsAction).get(str(chat_id))
     ret = None
     if action_topic:
         ret = action_topic.action_topic

     SESSION.close()
     return ret


 def del_action_topic(chat_id: int) -> bool:
     with INSERTION_LOCK:
         action_topic = SESSION.query(TopicsAction).get(str(chat_id))
         if action_topic:
             SESSION.delete(action_topic)
             SESSION.commit()
             return True
         else:
             SESSION.close()
             return False
"""
