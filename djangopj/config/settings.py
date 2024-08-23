"""
Django settings for project project.

Generated by 'django-admin startproject' using Django 4.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os
import mimetypes

# プロジェクトのベースディレクトリ
BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET_KEYを環境変数から取得
SECRET_KEY = os.environ.get("SECRET_KEY")

# DEBUGモードを環境変数から取得
DEBUG = os.environ.get("DEBUG") == "True"

# 許可するホストを環境変数から取得
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS").split(" ")

# アプリケーション定義
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.user.apps.UserConfig",
    "apps.DBmaint.apps.DbmaintConfig",
    "debug_toolbar",
    "rest_framework",
    "import_export",
    "simple_history",
    "rest_framework_api_key",
    "django.contrib.humanize",
]

# ミドルウェア定義
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
]

# ルートURL設定
ROOT_URLCONF = "config.urls"

# テンプレート設定
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
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

# WSGIアプリケーション
WSGI_APPLICATION = "config.wsgi.application"

# データベース設定
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_NAME"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
        "HOST": os.environ.get("POSTGRES_HOST", "db"),
        "PORT": os.environ.get("POSTGRES_PORT", 5432),
    }
}

# パスワードバリデーション
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# 国際化設定
LANGUAGE_CODE = "ja"
TIME_ZONE = "Asia/Tokyo"
USE_I18N = True
USE_TZ = True

# STATIC_ROOTを設定
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "/static/"


# 開発環境での静的ファイルの提供ディレクトリ
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# デフォルトのプライマリキーのフィールドタイプ
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# カスタムユーザーモデル
AUTH_USER_MODEL = "user.CustomUser"

# デバッグツールバーの内部IP設定
INTERNAL_IPS = ["127.0.0.1"]

# Django REST frameworkの設定
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 50,
}

# APIキーのカスタムヘッダー
API_KEY_CUSTOM_HEADER = "HTTP_X_API_KEY"

# これがないとDebug = Trueでcssが読み込めなくなる
mimetypes.add_type("text/css", ".css", True)
