# --- PERSONALIZADO: carga variables desde el archivo .env ---
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# --- PERSONALIZADO: SECRET_KEY  del .env ---
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-clave-solo-para-desarrollo')

# --- PERSONALIZADO: DEBUG  del .env ---
DEBUG = os.getenv('DEBUG') == 'True'

# --- PERSONALIZADO: permite cualquier host (ajustar en producción) ---
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    # Django por defecto
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # PERSONALIZADO: apps del negocio
    'usuarios',
    'catalogo',
    'almacenes',
    'movimientos',

    # PERSONALIZADO: librerias de terceros
    'rest_framework',        # API REST
    'drf_spectacular',       # documentación OpenAPI
    'drf_spectacular_sidecar', # sirve Swagger/ReDoc sin CDN externo
    'corsheaders',           # permite peticiones desde otros dominios
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # PERSONALIZADO: sirve archivos estáticos
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',       # PERSONALIZADO: habilita CORS
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'inventario.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'inventario.wsgi.application'

# --- PERSONALIZADO: cambiado de SQLite a PostgreSQL con credenciales del .env ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

# Django por defecto
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- PERSONALIZADO: cambiado de 'en-us' a español ---
LANGUAGE_CODE = 'es'

# --- PERSONALIZADO: cambiado de 'UTC' a Lima ---
TIME_ZONE = 'America/Lima'

USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'

# --- PERSONALIZADO: necesario para que collectstatic funcione en local y producción ---
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# --- PERSONALIZADO: whitenoise comprime y versiona los estáticos solo en producción ---
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- PERSONALIZADO: reemplaza el modelo de usuario por defecto de Django ---
AUTH_USER_MODEL = 'usuarios.Usuario'

# --- PERSONALIZADO: configuración global de Django REST Framework ---
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',  # integración con la documentación
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # autenticación por JWT
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',  # todos los endpoints requieren login
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,  # devuelve 10 registros por página
}

# --- PERSONALIZADO: metadatos y configuración de la documentación Swagger/ReDoc ---
SPECTACULAR_SETTINGS = {
    'TITLE': 'API de Inventario de Almacen',
    'DESCRIPTION': 'API REST para el control de productos, almacenes y movimientos de stock.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,  # oculta el endpoint /schema/ de la UI
    'SWAGGER_UI_DIST': 'SIDECAR',   # assets servidos localmente
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',
}

# --- PERSONALIZADO: duración de los tokens JWT ---
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),   # token de acceso: 2 horas
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),   # token de refresco: 7 días
}

# --- PERSONALIZADO: permite peticiones desde cualquier origen (ajustar en producción) ---
CORS_ALLOW_ALL_ORIGINS = True