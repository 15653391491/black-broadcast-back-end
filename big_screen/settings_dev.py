"""
Django settings for big_screen project.

Generated by 'django-admin startproject' using Django 1.11.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""
import os
import sys
import logging
import datetime
import djcelery
from celery import schedules

# from djcelery import schedulers

today = datetime.datetime.now().strftime('%Y-%m-%d')
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/
# LOG_DIR = os.path.dirname(os.path.dirname(os.path.dirname(BASE_DIR))) + '/log/'
LOG_DIR = os.path.dirname(BASE_DIR) + '/log/'
LOGBAK_DIR = os.path.dirname(BASE_DIR) + '/logBak/'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'i9d&m+l+zc6)woso(_%z*erl3^k8@_5zbg!zzn07b(34u5$&$@'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # ''
    'con_bigData.apps.MainConfig',
    'bigScreen.apps.BigscreenConfig',
    'con_brocast.apps.BrocastConfig',
    'con_control.apps.ControlConfig',
    'whiteList.apps.WhitelistConfig',
    'con_setting.apps.IsworkonConfig',
    'login.apps.LoginConfig',
    'mobile.apps.MobileConfig',
    'version.apps.VersionConfig',
    # ''
    'rest_framework',
    'djcelery',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'mobile.middlewares.MD1'
    # 'dwebsocket.middleware.WebSocketMiddleware'
]

# WEBSOCKET_ACCEPT_ALL = True
ROOT_URLCONF = 'big_screen.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'temple')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'big_screen.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'big_screen',
        'USER': 'root',
        'PASSWORD': 'mysql',
        'HOST': '124.70.44.128',
        # 'HOST': 'localhost',
        'PORT': '3306',
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/d/static/'
STATIC_BASE_DIR = os.path.dirname(os.path.dirname(BASE_DIR))
STATICFILES_DIRS = [os.path.join(STATIC_BASE_DIR, "static"), ]
CACHES = {
    "default": {  # 默认
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "session": {  # session
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "isworking": {  # 心跳包
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "massmark": {  # 海量点
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/3",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "broadcast": {  # 黑广播缓存
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/4",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "chart": {  # 首页图表数据
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/4",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "whdis": {  # 首页图表数据
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/6",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "mob-list": {  # 首页图表数据
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/4",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "object": {  # 首页图表数据
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/7",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "session"

# 日志
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {  # 格式化
        'console': {
            'format': '%(levelname)s %(asctime)s %(pathname)s %(lineno)d %(message)s',
            'datefmt': '%Y-%m-%d-%H-%M-%S'
        },
        'InfoFormat': {
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
            'datefmt': '%Y-%m-%d-%H-%M-%S'
        }
    },
    'handlers': {  # 处理器
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'console'
        },
        'file': {
            'level': 'INFO',
            'filename': LOG_DIR + 'file.log',  # 向数据库保存数据，
            # 指定日志文件大小，若超过指定的文件大小，会再生成一个新的日志文件保存日志信息
            'class': 'logging.handlers.RotatingFileHandler',
            # 指定文件大小
            # 1M=1024kb 1kb=1024b
            'maxBytes': 5 * 1024 * 1024,
            'formatter': 'InfoFormat'
        },
        'Bak': {
            'level': 'INFO',
            'filename': LOGBAK_DIR + 'bak' + '.log',  # 黑广播，
            # 指定日志文件大小，若超过指定的文件大小，会再生成一个新的日志文件保存日志信息
            'class': 'logging.handlers.RotatingFileHandler',
            # 指定文件大小
            # 1M=1024kb 1kb=1024b
            'maxBytes': 5 * 1024 * 1024,
            'formatter': 'InfoFormat'
        },
        'request': {
            'level': 'INFO',
            'filename': LOGBAK_DIR + 'request' + '.log',  # 黑广播，
            # 指定日志文件大小，若超过指定的文件大小，会再生成一个新的日志文件保存日志信息
            'class': 'logging.handlers.RotatingFileHandler',
            # 指定文件大小
            # 1M=1024kb 1kb=1024b
            'maxBytes': 5 * 1024 * 1024,
            'formatter': 'InfoFormat'
        },
    },
    'loggers': {  # 记录器
        'console': {
            'handlers': ['console', 'Bak'],
            'level': 'INFO',
            'propagate': False
        },
        'Process': {
            'handlers': ['file', 'Bak'],  # 指定file handler处理器，表示只写入到文件
            'level': 'DEBUG',
            'propagate': True,
        },
        'Lnglat': {
            'handlers': ['file', 'Bak'],  # 指定file handler处理器，表示只写入到文件
            'level': 'DEBUG',
            'propagate': True,
        },
        'Heartbeat': {
            'handlers': ['file', 'Bak'],  # 指定file handler处理器，表示只写入到文件
            'level': 'DEBUG',
            'propagate': True,
        },
        'Broadcasting': {
            'handlers': ["request"],  # 指定file handler处理器，表示只写入到文件
            'level': 'DEBUG',
            'propagate': True,
        },
        'Whitelist': {
            'handlers': ['file', 'Bak'],  # 指定file handler处理器，表示只写入到文件
            'level': 'DEBUG',
            'propagate': True,
        },
        'request': {
            'handlers': ['request'],  # 指定file handler处理器，表示只写入到文件
            'level': 'DEBUG',
            'propagate': True,
        },
        'body': {
            'handlers': ['request'],  # 指定file handler处理器，表示只写入到文件
            'level': 'DEBUG',
            'propagate': True,
        },
        'record': {
            'handlers': ['file'],  # 指定file handler处理器，表示只写入到文件
            'level': 'INFO',
            'propagate': True,
        },
        'mobile': {
            'handlers': ['file'],  # 指定file handler处理器，表示只写入到文件
            'level': 'INFO',
            'propagate': True,
        }
    }
}

#############################
# celery 配置信息 start
#############################


# 如果USE_TZ设置为True时，Django会使用系统默认设置的时区，此时的TIME_ZONE不管有没有设置都不起作用
# 如果USE_TZ 设置为False,TIME_ZONE = 'Asia/Shanghai', 则使用上海的UTC时间。
CELERY_TIMEZONE = TIME_ZONE
DJANGO_CELERY_BEAT_TZ_AWARE = False
djcelery.setup_loader()
BROKER_URL = 'redis://127.0.0.1:6379/5'
CELERY_IMPORTS = ('bigScreen.tasks', 'con_bigData.tasks', "mobile.tasks")

CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'

CELERYBEAT_SCHEDULE = {  # 定时器策略
    # 定时任务一：　每隔一小时运行一次
    u'首页图表': {
        "task": "bigScreen.tasks.set_bigscreen_chart",
        "schedule": schedules.timedelta(hours=2),
        "args": (),
    },
    u'数据中心图表': {
        "task": "con_bigData.tasks.save_chart_data",
        "schedule": schedules.timedelta(hours=24),
        "args": (),
    },
    u'数据中心热力图': {
        "task": "con_bigData.tasks.heat_map_data",
        "schedule": schedules.timedelta(hours=24),
        "args": (),
    },
    u'清理过期黑广播数据': {
        "task": "mobile.tasks.expire_broadcast",
        "schedule": schedules.timedelta(minutes=1),
        "args": (),
    },
    u'清理过期心跳包': {
        "task": "mobile.tasks.pop_heartbeat",
        "schedule": schedules.timedelta(minutes=1),
        "args": (),
    },
}
#############################
# celery 配置信息 end
#############################
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880
CELERY_WORKER_CONCURRENCY = 5
CELERY_WORKER_MAX_TASKS_PER_CHILD = 200

LOGIN_URL = 'login.html'

WEBSOCKET_FACTORY_CLASS = 'dwebsocket.backends.uwsgi.factory.uWsgiWebSocketFactory'
