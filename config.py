from datetime import timedelta

# mysql
HOST = '127.0.0.1'  # 124.222.67.216 127.0.0.1
PORT = '3306'
DATABASE = 'webgis_nefu'
USERNAME = 'root' # webgis_nefu root
PASSWORD = '2618'
CHARSET = 'utf8mb4'
DB_URI = f'mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}?charset={CHARSET}'
SQLALCHEMY_DATABASE_URI = DB_URI

# flask_login
# SESSION_SECRET_KEY = 'xiaoruiruiecho'

# jwt
JWT_SECRET_KEY = 'xiaoruiruiecho'
JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=30)

# redis
REDIS_PASSWORD = ''
REDIS_URL = f'redis://localhost:6379/0' # 'redis://:{REDIS_PASSWORD}@localhost:6379/0'
