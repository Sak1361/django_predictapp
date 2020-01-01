from socket import gethostname
import os

# settings.pyからそのままコピー
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = '&02n-2@66o#w+h-92gd(da-*zc5bgp7l-l5g1siq1p5)aosu&c'
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'predictions/static')

hostname = gethostname()
if "Sak1361-mac" in hostname:  # ローカル の場合
    DEBUG = True  # ローカルでDebug
    import pymysql
    pymysql.install_as_MySQLdb()
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'django_predict',  # DB name
            'USER': 'root',
            "HOST": "127.0.0.1",
            "PORT": "3306",
            'OPTIONS': {
                # 'read_default_file': '/path/to/my.cnf',
                'init_command': 'SET default_storage_engine=INNODB',
            },
        }
    }
    ALLOWED_HOSTS = []
else:
     # 本番環境
    DEBUG = True
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
            },
        },
    }

    # DB設定
    import dj_database_url
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    db_from_env = dj_database_url.config()
    DATABASES = {
        'default': dj_database_url.config()
    }
    ALLOWED_HOSTS = ['*']
