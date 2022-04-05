def incr_likes_count(sender, instance, created, **kwargs):
    from tweets.models import Tweet
    from django.db.models import F
    from utils.redis_helper import RedisHelper

    if not created:
        return

    model_class = instance.content_type.model_class()
    if model_class != Tweet:
        # TODO HOMEWORK 给 Comment 使用类似的方法进行 likes_count 的统计
        return

    # 不可以使用
    # tweet.likes_count += 1
    # tweet.save()
    # 因此这个操作不是原子操作，必须使用 update 语句才是原子操作
    # SQL query:
    # UPDATE likes_count = likes_count + 1 FROM tweets_table where id=<instance.object_id>
    # 方法1
    # 有弊端，update 方法不触发 pre_save 信号，会有问题
    # Tweet.objects.filter(
    #     id=instance.object_id,
    # ).update(likes_count=F('likes_count') + 1)
    # 方法2
    Tweet.objects.filter(id=instance.object_id).update(likes_count=F('likes_count') + 1)
    RedisHelper.incr_count(instance.content_object, 'likes_count')


def decr_likes_count(sender, instance, **kwargs):
    from tweets.models import Tweet
    from django.db.models import F
    from utils.redis_helper import RedisHelper

    model_class = instance.content_type.model_class()
    if model_class != Tweet:
        # TODO HOMEWORK 给 Comment 使用类似的方法进行 likes_count 的统计
        return

    # handle tweet likes cancel
    Tweet.objects.filter(id=instance.object_id).update(likes_count=F('likes_count') - 1)
    RedisHelper.decr_count(instance.content_object, 'likes_count')
