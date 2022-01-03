from django.contrib.auth.models import User
from rest_framework import exceptions
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class UserSerializerForTweet(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class UserSerializerForLike(UserSerializerForTweet):
    pass


class UserSerializerForComment(UserSerializerForTweet):
    pass


class UserSerializerForFriendship(UserSerializerForTweet):
    pass


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        if not User.objects.filter(username=data['username'].lower()).exists():
            raise exceptions.ValidationError({
                'username': 'User does not exist.'
            })
        return data


class SignupSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=20, min_length=6)
    password = serializers.CharField(max_length=20, min_length=6)
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    # will be called when is_valid is called
    def validate(self, data):
        # TODO<HOMEWORK> 增加验证 username 是不是只由给定的字符集合构成
        for character in data['username']:
            if character.isalpha() or character.isdigit() or character in "_":
                continue
            raise exceptions.ValidationError({
                'username': 'This username contains invalid character.'
            })
        # 检查用户名是否存在
        # case_insensitive
        if User.objects.filter(username=data['username'].lower()).exists():
            raise exceptions.ValidationError({
                'username': 'This username has been occupied.'
            })
        # 检查邮箱是否已被占用
        if User.objects.filter(email=data['email'].lower()).exists():
            raise exceptions.ValidationError({
                'email': 'This email address has been occupied.'
            })
        validated_data = dict(data)
        validated_data['email'] = data['email'].lower()
        validated_data['username'] = data['username'].lower()
        return validated_data

    def create(self, validated_data):
        username = validated_data['username']
        email = validated_data['email']
        password = validated_data['password']
        # create_user 是 django 帮忙定义的，你自己的类是没有这个函数的
        user = User.objects.create_user(
            username=username,
            email=email,
            # 这里 create_user 自带了加密 password
            password=password,
        )
        return user
