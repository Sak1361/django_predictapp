import pymysql
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

DEBUG = True
