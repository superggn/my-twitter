from rest_framework import serializers

from newsfeeds.models import NewsFeed
from tweets.api.serializers import TweetSerializer


class NewsFeedSerializer(serializers.ModelSerializer):
    # 这里 TweetSerializer 需要的参数增加了一个 context
    #  所以对应的 NewsFeedSerializer 也需要传入 context
    tweet = TweetSerializer()

    class Meta:
        model = NewsFeed
        fields = ('id', 'created_at', 'user', 'tweet')
