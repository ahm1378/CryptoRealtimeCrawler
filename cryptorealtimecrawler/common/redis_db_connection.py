import jsons
import redis


class RedisConnection:
    def __init__(self,host, port):
        redis_realtime_db_host = host
        self.__redis = redis.Redis(host=redis_realtime_db_host, port=port, decode_responses=True)

    def inc(self, key):
        self.__redis.incr(key)

    def expire(self, key, period):
        self.__redis.expire(key, period)

    def set(self, key, value, ex=None):
        json_data = jsons.dumps(value, {'ensure_ascii': False})
        if ex:
            self.__redis.set(key, json_data, ex=ex)
        else:
            self.__redis.set(key, json_data)

    def set_with_expiry(self, key, value, expiry):
        self.__redis.setex(key, expiry, value)

    def update_redis_field(self, key, field_names, new_values):
        """
        Update a specific field in a dictionary stored in Redis.

        :param redis_handler: Redis connection object
        :param key: The key under which the dictionary is stored in Redis
        :param field_name: The field within the dictionary to update
        :param new_value: The new value to set for the specified field
        """
        data = self.get(key=key)
        for i in range(len(field_names)):
            data[field_names[i]]=new_values[i]
        self.set(key=key,value=data)

    def bulk_set(self, data_dict: dict):
        pipe = self.__redis.pipeline()
        for key in data_dict.keys():
            pipe.set(key, jsons.dumps(data_dict[key], {'ensure_ascii': False}))

        pipe.execute()

    def get(self, key, cls=None, raw=False):
        data = self.__redis.get(key)
        if data:
            try:
                return jsons.loads(data)
            except:
                return data
        else:
            return False

    def delete_key(self,key):
        data = self.__redis.delete(key)

    def publish(self, channel, data):
        json_data = jsons.dumps(data, {'ensure_ascii': False})
        self.__redis.publish(channel, json_data)

    def subscribe(self, channel, callback_function):
        pubsub = self.__redis.pubsub()
        pubsub.subscribe(**{channel: callback_function})
        pubsub.run_in_thread(sleep_time=0.01)

    def check_redis_key_existence(self, key):
        return self.__redis.exists(key)

    def bulk_get(self, keys: list) -> dict:
        """
        Get multiple key values simultaneously using pipeline

        Args:
            keys (list): List of keys we want to get their values

        Returns:
            dict: Dictionary of keys and values. Keys that don't exist won't be in the output
        """
        if not keys:
            return {}
            
        # Use pipeline to get data simultaneously
        pipe = self.__redis.pipeline()
        for key in keys:
            pipe.get(key)
            
        # Execute commands and get results
        results = pipe.execute()
        
        # Convert results to dictionary and remove None values
        data = {}
        for key, value in zip(keys, results):
            if value is not None:
                try:
                    data[key] = jsons.loads(value)
                except:
                    data[key] = value
                    
        return data
