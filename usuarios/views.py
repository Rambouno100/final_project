from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import UsuarioSerializer, LoginSerializer


@extend_schema(tags=['Autenticacion'])
@extend_schema_view(
    post=extend_schema(
        summary='Registrar un usuario',
        description='Crea un usuario nuevo. Es la unica ruta publica junto con el login.'
    )
)
class RegistroView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [AllowAny]


@extend_schema(tags=['Autenticacion'])
@extend_schema_view(
    post=extend_schema(
        summary='Iniciar sesion',
        description='Devuelve el par de tokens access y refresh.'
    )
)
class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]


@extend_schema(tags=['Autenticacion'])
@extend_schema_view(
    post=extend_schema(
        summary='Renovar el access token',
        description='Entrega un access nuevo a partir de un refresh valido.'
    )
)
class RefreshView(TokenRefreshView):
    permission_classes = [AllowAny]


@extend_schema(tags=['Usuarios'])
@extend_schema_view(
    get=extend_schema(
        summary='Listar usuarios',
        description='Lista paginada de los usuarios activos del sistema.'
    ),
    post=extend_schema(
        summary='Crear un usuario desde el sistema',
        description='Igual que el registro, pero exige estar autenticado. Se usa cuando el '
                    'encargado da de alta a un trabajador en lugar de que se registre solo.'
    ),
)
class UsuarioListView(generics.ListCreateAPIView):
    serializer_class = UsuarioSerializer

    def get_queryset(self):
        consulta = get_user_model().objects.filter(is_active=True)
        area = self.request.query_params.get('area')
        if area:
            consulta = consulta.filter(area=area.upper())
        return consulta.order_by('username')


@extend_schema(tags=['Usuarios'])
@extend_schema_view(
    get=extend_schema(summary='Obtener un usuario por su ID'),
    put=extend_schema(summary='Actualizar un usuario'),
    patch=extend_schema(summary='Actualizar parcialmente un usuario'),
    delete=extend_schema(
        summary='Desactivar un usuario',
        description='No borra la fila, solo marca is_active en False para no perder el historial.'
    ),
)
class UsuarioDetalleView(generics.RetrieveUpdateDestroyAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UsuarioSerializer

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
