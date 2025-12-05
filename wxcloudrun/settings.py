import os
from pathlib import Path
import time

CUR_PATH = os.path.dirname(os.path.realpath(__file__))
LOG_PATH = os.path.join(os.path.dirname(CUR_PATH), "logs")  # LOG_PATH是存放日志的路径
if not os.path.exists(LOG_PATH):
    os.mkdir(LOG_PATH)  # 如果不存在这个logs文件夹，就自动创建一个

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-_&03zc)d*3)w-(0grs-+t-0jjxktn7k%$3y6$9=x_n_ibg4js6"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "drf_yasg",  # Swagger/OpenAPI 文档
    "wxcloudrun",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    # 'django.middleware.csrf.CsrfViewMiddleware',
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "wxcloudrun.middleware.CloudbaseAuthMiddleware",  # 云托管身份认证
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "wxcloudrun.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "wxcloudrun.wsgi.application"

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

# 优先使用 MySQL，如果未配置环境变量则使用 SQLite
MYSQL_ADDRESS = os.environ.get("MYSQL_ADDRESS")

if MYSQL_ADDRESS:
    # 生产环境使用 MySQL
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.environ.get("MYSQL_DATABASE", "petbaodb"),
            "USER": os.environ.get("MYSQL_USERNAME", "root"),
            "HOST": MYSQL_ADDRESS.split(":")[0],
            "PORT": MYSQL_ADDRESS.split(":")[1],
            "PASSWORD": os.environ.get("MYSQL_PASSWORD"),
            "OPTIONS": {"charset": "utf8mb4"},
        }
    }
else:
    # 开发环境使用 SQLite
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        # 日志格式
        "standard": {
            "format": "[%(asctime)s] [%(filename)s:%(lineno)d] [%(module)s:%(funcName)s] "
            "[%(levelname)s]- %(message)s"
        },
        "simple": {"format": "%(levelname)s %(message)s"},  # 简单格式
    },
    # 过滤
    "filters": {},
    # 定义具体处理日志的方式
    "handlers": {
        # 默认记录所有日志
        "default": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(
                LOG_PATH, "all-{}.log".format(time.strftime("%Y-%m-%d"))
            ),
            "maxBytes": 1024 * 1024 * 5,  # 文件大小
            "backupCount": 5,  # 备份数
            "formatter": "standard",  # 输出格式
            "encoding": "utf-8",  # 设置默认编码，否则打印出来汉字乱码
        },
        # 输出错误日志
        "error": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(
                LOG_PATH, "error-{}.log".format(time.strftime("%Y-%m-%d"))
            ),
            "maxBytes": 1024 * 1024 * 5,  # 文件大小
            "backupCount": 5,  # 备份数
            "formatter": "standard",  # 输出格式
            "encoding": "utf-8",  # 设置默认编码
        },
        # 控制台输出
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        # 输出info日志
        "info": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(
                LOG_PATH, "info-{}.log".format(time.strftime("%Y-%m-%d"))
            ),
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 5,
            "formatter": "standard",
            "encoding": "utf-8",  # 设置默认编码
        },
    },
    # 配置用哪几种 handlers 来处理日志
    "loggers": {
        # 类型 为 django 处理所有类型的日志， 默认调用
        "django": {
            "handlers": ["default", "console"],
            "level": "INFO",
            "propagate": False,
        },
        # log 调用时需要当作参数传入
        "log": {
            "handlers": ["error", "info", "console", "default"],
            "level": "INFO",
            "propagate": True,
        },
    },
}

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/static/"

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGS_DIR = "/data/logs/"

# Custom User Model
AUTH_USER_MODEL = "wxcloudrun.User"

# CORS Settings
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# REST Framework Settings
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        # 云托管认证：使用中间件设置的用户
        "wxcloudrun.authentication.CloudbaseAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        # 默认允许所有访问，在各个 ViewSet 中单独控制权限
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}

# JWT Settings
from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=7),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
}

# WeChat Mini Program Settings
WECHAT_APPID = os.environ.get("WECHAT_APPID", "")
WECHAT_SECRET = os.environ.get("WECHAT_SECRET", "")

# Media files (for uploaded images/videos)
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Swagger/OpenAPI Settings
SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT token，格式: Bearer {token}",
        }
    },
    "USE_SESSION_AUTH": False,
    "JSON_EDITOR": True,
    "SUPPORTED_SUBMIT_METHODS": ["get", "post", "put", "delete", "patch"],
    "OPERATIONS_SORTER": "alpha",
    "TAGS_SORTER": "alpha",
    "DOC_EXPANSION": "none",
    "DEEP_LINKING": True,
    "SHOW_EXTENSIONS": True,
    "DEFAULT_MODEL_RENDERING": "example",
}
