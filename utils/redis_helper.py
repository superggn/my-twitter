from django.conf import settings
from utils.redis_client import RedisClient
from utils.redis_serializers import DjangoModelSerializer


class RedisHelper:

    @classmethod
    def _load_objects_to_cache(cls, key, objects):
        conn = RedisClient.get_connection()

        serialized_list = []
        # 最多只 cache REDIS_LIST_LENGTH_LIMIT 那么多个 objects
        # 超过这个限制的 objects，就去数据库里读取。一般这个限制会比较大，比如 1000
        # 因此翻页翻到 1000 的用户访问量会比较少，从数据库读取也不是大问题
        for obj in objects[:settings.REDIS_LIST_LENGTH_LIMIT]:
            serialized_data = DjangoModelSerializer.serialize(obj)
            serialized_list.append(serialized_data)

        if serialized_list:
            # 注意，这里一次 rpush 就行，别 for 循环
            conn.rpush(key, *serialized_list)
            conn.expire(key, settings.REDIS_KEY_EXPIRE_TIME)

    @classmethod
    def load_objects(cls, key, queryset):
        """
        load object: 给 key, 从缓存里数据；如果缓存里没有，就从数据库里取数据
        """
        conn = RedisClient.get_connection()
        # 如果在 cache 里存在，则直接拿出来，然后返回
        if conn.exists(key):
            # 0, -1: 从第一个到最后一个，全查一遍
            serialized_list = conn.lrange(key, 0, -1)
            objects = []
            # deserialize
            for serialized_data in serialized_list:
                deserialized_obj = DjangoModelSerializer.deserialize(serialized_data)
                objects.append(deserialized_obj)
            return objects

        # cache miss
        cls._load_objects_to_cache(key, queryset)
        # 转换为 list 的原因是保持返回类型的统一，因为存在 redis 里的数pa据是 list 的形式
        return list(queryset)

    @classmethod
    def push_object(cls, key, obj, queryset):
        """
        push object: 把某一个 obj push 到缓存里去
        """
        conn = RedisClient.get_connection()
        if not conn.exists(key):
            # 如果 key 不存在，直接从数据库里 load
            # 就不走单个 push 的方式加到 cache 里了
            cls._load_objects_to_cache(key, queryset)
            return
        serialized_data = DjangoModelSerializer.serialize(obj)
        conn.lpush(key, serialized_data)
        # ltrim 参数： 希望保留的区间
        conn.ltrim(key, 0, settings.REDIS_LIST_LENGTH_LIMIT - 1)
