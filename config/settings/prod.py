"""Production settings. Secrets come from environment variables."""

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403
from .base import env

DEBUG = False

SECRET_KEY = env("DJANGO_SECRET_KEY")
if not SECRET_KEY or SECRET_KEY.startswith("unsafe-") or SECRET_KEY == "change-me-to-a-long-random-string":
    raise ImproperlyConfigured("Set DJANGO_SECRET_KEY to a strong random value.")

ALLOWED_HOSTS = [
    host.strip()
    for host in env("DJANGO_ALLOWED_HOSTS", "").split(",")
    if host.strip()
]
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured("Set DJANGO_ALLOWED_HOSTS.")

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in env("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env("DJANGO_SECURE_SSL_REDIRECT", "true").lower() in {"1", "true", "yes"}
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SECURE_HSTS_SECONDS = int(env("DJANGO_SECURE_HSTS_SECONDS", "31536000"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"

ADMIN_URL = env("DJANGO_ADMIN_URL", "manage/").strip("/") + "/"

STORAGES = {
    **STORAGES,
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}
