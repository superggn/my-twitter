from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from tweets.api.serializers import TweetCreateSerializer, TweetSerializer
from tweets.models import Tweet
from newsfeeds.services import NewsFeedService


class TweetViewSet(viewsets.GenericViewSet):
    # 原本还可以继承2个 viewset，我们自己实现，不用django的了
    # viewsets.mixins.CreateModelMixin,
    # viewsets.mixins.ListModelMixin):
    """
    API endpoint that allows users to create, list tweets
    """
    # queryset 都是自己写，暂时不指定了
    # queryset = Tweet.objects.all()
    # 调用 self.get_queryset() 的时候会找类上面声明的这个 queryset
    # 在这里声明的serializer 只在 debug 的时候会用到，就是 rest_framework
    #  的那个HTML form 界面，推荐每个函数自己指定 serializer class
    serializer_class = TweetCreateSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request):
        """
        重载 list 方法，不列出所有 tweets，必须要求指定 user_id 作为筛选条件
        """
        if 'user_id' not in request.query_params:
            return Response('missing user_id', status=400)

        # 这句查询会被翻译为
        # select * from twitter_tweets
        # where user_id = xxx
        # order by created_at desc
        # 这句 SQL 查询会用到 user 和 created_at 的联合索引
        # 单纯的 user 索引是不够的
        tweets = Tweet.objects.filter(
            user_id=request.query_params['user_id']
        ).order_by('-created_at')
        # 返回 list of dict
        serializer = TweetSerializer(tweets, many=True)
        # 一般来说 json 格式的 response 默认都要用 hash 的格式
        # 而不能用 list 的格式（约定俗成）
        return Response({'tweets': serializer.data})

    def create(self, request, *args, **kwargs):
        """
        重载 create 方法，因为需要默认用当前登录用户作为 tweet.user
        """
        # 展示和创建用的是两个 serializer
        serializer = TweetCreateSerializer(
            data=request.data,
            context={'request': request},
        )
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': "Please check input",
                'errors': serializer.errors,
            }, status=400)
        # save will trigger create method in TweetSerializerForCreate
        tweet = serializer.save()
        NewsFeedService.fanout_to_followers(tweet)
        return Response(TweetSerializer(tweet).data, status=201)
