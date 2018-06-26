from swampdragon import route_handler
from swampdragon.route_handler import ModelPubRouter
from app.models import ChatRoom, Message, Attendee
from app.serializers import ChatRoomListSerializer, MessageItemSerializer


class ChatRoomListRouter(ModelPubRouter):
    route_name = 'chat-room-list'
    serializer_class = ChatRoomListSerializer
    model = ChatRoom

    def get_object(self, **kwargs):
        print(kwargs['id'])
        return self.model.objects.get(pk=kwargs['id'])

    def get_query_set(self, **kwargs):
        return self.model.objects.all()


class MessageItemRouter(ModelPubRouter):
    route_name = 'message-item'
    serializer_class = MessageItemSerializer
    model = Message

    def get_initial(self, verb, **kwargs):
        chat_room = ChatRoom.objects.get(pk=kwargs['chat_room_id'])
        text = kwargs['text']
        sender = Attendee.objects.get(pk=kwargs['sender_id'])
        return {'chat_room': chat_room, 'text': text, 'sender': sender}

    def get_object(self, **kwargs):
        return self.model.objects.get(pk=kwargs['id'])

    def get_query_set(self, **kwargs):
        return self.model.objects.filter(chat_room__id=kwargs['chat_room_id'])

route_handler.register(ChatRoomListRouter)
route_handler.register(MessageItemRouter)