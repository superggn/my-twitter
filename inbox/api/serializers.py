from notifications.models import Notification
from rest_framework import serializers

from accounts.api.serializers import UserSerializer


class NotificationSerializer(serializers.ModelSerializer):
    # 其实这个 recipient 不用加，反正都是当前登录用户...
    recipient = UserSerializer()

    class Meta:
        model = Notification
        fields = (
            'id',
            'recipient',
            'actor_content_type',
            'actor_object_id',
            'verb',
            'action_object_content_type',
            'action_object_object_id',
            'target_content_type',
            'target_object_id',
            'timestamp',
            'unread',
        )
