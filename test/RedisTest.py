import config
import unittest

from app import app
from flask_redis import FlaskRedis


class RedisTest(unittest.TestCase):

    def setUp(self):
        app.config.from_object(config)
        self.app = app

    # 必须以 test 开头
    def test_connect_to_redis(self):
        redis_client = FlaskRedis(app)

        print(redis_client)

        key1 = '1'
        value1 = '1'
        key2 = '2'

        redis_client.set(key1, value1)

        print(redis_client.get(key1))
        print(redis_client.get(key2))


if __name__ == '__main__':
    unittest.main()
