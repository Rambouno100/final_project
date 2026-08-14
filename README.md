# API de Inventario de Almacen

API REST para controlar productos, almacenes y movimientos de stock (entradas, salidas y
traslados). Hecha con Django + Django REST Framework, PostgreSQL y autenticacion JWT.

## Stack

| Pieza | Que se uso |
|---|---|
| Framework | Django 6.0 + Django REST Framework |
| ORM | Django ORM |
| Base de datos | PostgreSQL |
| Autenticacion | JWT (`djangorestframework-simplejwt`) |
| Documentacion | Swagger / Redoc (`drf-spectacular`) |
| Pruebas | pytest + pytest-django + Faker |
| Despliegue | Render (gunicorn + whitenoise) |

## Estructura

```
backendv2/
├── inventario/          configuracion del proyecto (settings, urls, wsgi)
├── core/                modelo base abstracto: timestamps + borrado logico
├── usuarios/            registro, login JWT y CRUD de usuarios
├── catalogo/            categorias y productos
├── almacenes/           almacenes y stock por almacen
├── movimientos/         movimientos de stock y su detalle
├── tests/               pruebas con pytest
├── build.sh             script de despliegue en Render
├── manage.py
├── pytest.ini
└── requirements.txt
```

Cada app repite siempre los mismos cinco archivos: `models.py`, `serializers.py`,
`views.py`, `urls.py`, `admin.py`. No hay ningun archivo que exista en una app y no en
las otras, asi que si entiendes una entiendes las cuatro.

## Instalacion local

Requisitos: Python 3.12 o superior y PostgreSQL corriendo en localhost.

```bash
# 1. Crear la base de datos vacia
psql -U postgres -c "CREATE DATABASE inventario_v2;"

# 2. Entorno virtual
python -m venv entorno
entorno\Scripts\activate          # en Windows
pip install -r requirements.txt

# 3. Variables de entorno
copy .env.example .env            # y ajustar la contrasena de postgres

# 4. Migraciones
python manage.py makemigrations
python manage.py migrate

# 5. Datos de ejemplo (opcional pero recomendado para la demo)
python manage.py datos_demo

# 6. Levantar
python manage.py runserver
```

Documentacion interactiva: <http://127.0.0.1:8000/api/docs/swagger/>


## Endpoints

Todas las rutas cuelgan de `/api/v1/`. Solo el registro, el login y el refresh son publicas;
el resto exige el header `Authorization: Bearer <access>`.

### Autenticacion
| Metodo | Ruta | Que hace |
|---|---|---|
| POST | `/auth/registro/` | Crea un usuario |
| POST | `/auth/login/` | Devuelve `access` y `refresh` |
| POST | `/auth/refresh/` | Renueva el `access` |

### Usuarios
| Metodo | Ruta |
|---|---|
| GET / POST | `/usuarios/` (filtro `?area=ALMACEN`) |
| GET / PUT / PATCH / DELETE | `/usuarios/{id}/` |

### Catalogo
| Metodo | Ruta |
|---|---|
| GET / POST | `/categorias/` |
| GET / PUT / PATCH / DELETE | `/categorias/{id}/` |
| GET | `/categorias/{id}/productos/` |
| GET / POST | `/productos/` (filtro `?buscar=` o `?categoria=`, no los dos a la vez) |
| GET / PUT / PATCH / DELETE | `/productos/{id}/` |

### Almacenes
| Metodo | Ruta |
|---|---|
| GET / POST | `/almacenes/` |
| GET / PUT / PATCH / DELETE | `/almacenes/{id}/` |
| GET | `/almacenes/{id}/stock/` |
| GET / POST | `/stock/` (filtro `?almacen=`) |
| GET / PUT / PATCH / DELETE | `/stock/{id}/` |

### Movimientos
| Metodo | Ruta |
|---|---|
| GET / POST | `/movimientos/` (filtros `?tipo=` y `?estado=`) |
| GET | `/movimientos/resumen/` agrupado por estado |
| GET / PUT / PATCH / DELETE | `/movimientos/{id}/` |
| PUT | `/movimientos/{id}/estado/` confirmar o anular |

## Como funciona el negocio

Un movimiento nace en estado `BORRADOR` y **no toca el stock**. Recien cuando se manda
`PUT /movimientos/{id}/estado/` con `{"estado": "CONFIRMADO"}` se descuenta del almacen de
origen y se suma al de destino, todo dentro de una transaccion.

- `ENTRADA`: solo almacen de destino (compra, devolucion).
- `SALIDA`: solo almacen de origen (despacho, consumo).
- `TRASLADO`: los dos, y tienen que ser distintos.

Si el stock del origen no alcanza, la confirmacion responde 400 y nada se modifica.
Un movimiento confirmado ya no se puede editar ni borrar, solo anular.

## Despliegue en Render

1. Subir el repositorio a GitHub. Antes del push, marcar el script como ejecutable:
   ```bash
   git update-index --chmod=+x build.sh
   ```
   El `.gitattributes` ya se encarga de que `build.sh` viaje con saltos de linea de Linux;
   sin eso Render responde `bad interpreter` y el deploy falla.
2. En Render crear **New > PostgreSQL** y anotar las credenciales.
3. Crear **New > Web Service** apuntando al repositorio, con:
   - Build Command: `./build.sh`
   - Start Command: `gunicorn inventario.wsgi:application`
4. En **Environment** cargar las variables:

   | Variable | Valor |
   |---|---|
   | `SECRET_KEY` | una clave larga cualquiera |
   | `DEBUG` | `False` |
   | `DB_NAME` | de la base de Render |
   | `DB_USER` | de la base de Render |
   | `DB_PASSWORD` | de la base de Render |
   | `DB_HOST` | el *Internal Database URL host* |
   | `DB_PORT` | `5432` |

5. Al terminar el deploy, la documentacion queda en
   `https://<tu-servicio>.onrender.com/api/docs/swagger/`.

