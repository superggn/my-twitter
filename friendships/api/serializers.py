from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from accounts.api.serializers import UserSerializerForFriendship
from friendships.models import Friendship
from friendships.services import FriendshipService


class FriendshipSerializerForCreate(serializers.ModelSerializer):
    from_user_id = serializers.IntegerField()
    to_user_id = serializers.IntegerField()

    class Meta:
        model = Friendship
        fields = ('from_user_id', 'to_user_id')

    def validate(self, attrs):
        if attrs['from_user_id'] == attrs['to_user_id']:
            raise ValidationError({
                'message': 'You can not follow yourself.',
            })
        if not User.objects.filter(id=attrs['to_user_id']).exists():
            raise ValidationError({
                'message': 'You can not follow an un-exist user.',
            })
        if Friendship.objects.filter(
                from_user_id=attrs['from_user_id'],
                to_user_id=attrs['to_user_id'],
        ).exists():
            raise ValidationError({
                'message': 'You has already followed this user.',
            })
        return attrs

    def create(self, validated_data):
        from_user_id = validated_data['from_user_id']
        to_user_id = validated_data['to_user_id']
        return Friendship.objects.create(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
        )


# 可以通过 source=xxx 指定去访问每个 model instance 的 xxx 方法
# 即 model_instance.xxx 来获得数据
# https://www.django-rest-framework.org/api-guide/serializers/#specifying-fields-explicitly
class FollowerSerializer(serializers.ModelSerializer):
    # 这里的 source=xxx: 外键通过哪个字段（/方法）去取
    user = UserSerializerForFriendship(source='from_user')
    has_followed = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ('user', 'created_at', 'has_followed')

    def get_has_followed(self, obj):
        if self.context['request'].user.is_anonymous:
            return False
        # <TODO> 这个部分会对每个 object 都去执行一次 SQL 查询，速度会很慢，如何优化呢？
        # 我们将在后序的课程中解决这个问题
        return FriendshipService.has_followed(self.context['request'].user, obj.from_user)


class FollowingSerializer(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source='to_user')
    has_followed = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ('user', 'created_at', 'has_followed')

    def get_has_followed(self, obj):
        if self.context['request'].user.is_anonymous:
            return False

        # <TODO> 这个部分会对每个 object 都去执行一次 SQL 查询，速度会很慢，如何优化呢？
        # 我们将在后序的课程中解决这个问题
        return FriendshipService.has_followed(self.context['request'].user, obj.to_user)
