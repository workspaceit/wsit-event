from swampdragon.serializers.model_serializer import ModelSerializer


class AttendeeSerializer(ModelSerializer):
    class Meta:
        model = 'app.Attendee'


class ChatRoomListSerializer(ModelSerializer):
    class Meta:
        model = 'app.ChatRoom'
        publish_fields = ('id',)


class MessageItemSerializer(ModelSerializer):
    sender = 'AttendeeSerializer'

    class Meta:
        model = 'app.Message'

