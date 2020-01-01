import os

# settings.pyからそのままコピー
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = '&02n-2@66o#w+h-92gd(da-*zc5bgp7l-l5g1siq1p5)aosu&c'

# settings.pyからそのままコピー
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'django_predict',  # DB name
        'USER': 'root',
        'HOST': '',
        'POST': '',
        'OPTIONS': {
            # 'read_default_file': '/path/to/my.cnf',
            'init_command': 'SET default_storage_engine=INNODB',
        },
    }
}
DEBUG = True  # ローカルでDebugできるようになります
