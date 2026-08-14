from django.db.models import Q
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import generics, serializers

from .models import Categoria, Producto
from .serializers import CategoriaSerializer, ProductoSerializer


@extend_schema(tags=['Categorias'])
@extend_schema_view(
    get=extend_schema(summary='Listar categorias'),
    post=extend_schema(summary='Registrar una categoria'),
)
class CategoriaView(generics.ListCreateAPIView):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer


@extend_schema(tags=['Categorias'])
@extend_schema_view(
    get=extend_schema(summary='Obtener una categoria por su ID'),
    put=extend_schema(summary='Actualizar una categoria'),
    patch=extend_schema(summary='Actualizar parcialmente una categoria'),
    delete=extend_schema(
        summary='Eliminar logicamente una categoria',
        description='No se puede eliminar una categoria que todavia tiene productos.'
    ),
)
class CategoriaDetalleView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

    def perform_destroy(self, instance):
        if instance.productos.exists():
            raise serializers.ValidationError(
                'La categoria tiene productos activos. Muevelos o eliminalos primero.'
            )
        instance.eliminar_logico()


@extend_schema(
    tags=['Productos'],
    parameters=[
        OpenApiParameter('buscar', str, description='Filtra por codigo o nombre del producto.'),
        OpenApiParameter(
            'categoria', int,
            description='Filtra por el ID de la categoria. Se ignora si tambien se envia "buscar".'
        ),
    ],
)
@extend_schema_view(
    get=extend_schema(summary='Listar productos'),
    post=extend_schema(summary='Registrar un producto'),
)
class ProductoView(generics.ListCreateAPIView):
    serializer_class = ProductoSerializer

    def get_queryset(self):
        consulta = Producto.objects.select_related('categoria')
        buscar = self.request.query_params.get('buscar')
        categoria = self.request.query_params.get('categoria')
        if buscar:
            return consulta.filter(Q(nombre__icontains=buscar) | Q(codigo__icontains=buscar))
        if categoria:
            return consulta.filter(categoria_id=categoria)
        return consulta


@extend_schema(tags=['Productos'])
@extend_schema_view(
    get=extend_schema(summary='Obtener un producto por su ID'),
    put=extend_schema(summary='Actualizar un producto'),
    patch=extend_schema(summary='Actualizar parcialmente un producto'),
    delete=extend_schema(
        summary='Eliminar logicamente un producto',
        description='No se puede eliminar un producto que todavia tiene stock en algun almacen.'
    ),
)
class ProductoDetalleView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Producto.objects.select_related('categoria')
    serializer_class = ProductoSerializer

    def perform_destroy(self, instance):
        if instance.stocks.filter(cantidad__gt=0).exists():
            raise serializers.ValidationError(
                'El producto todavia tiene stock. Registra la salida antes de eliminarlo.'
            )
        instance.eliminar_logico()


@extend_schema(tags=['Categorias'])
@extend_schema_view(
    get=extend_schema(
        summary='Listar los productos de una categoria',
        description='Devuelve los productos activos que pertenecen a la categoria indicada.'
    )
)
class CategoriaProductosView(generics.ListAPIView):
    serializer_class = ProductoSerializer

    def get_queryset(self):
        return Producto.objects.filter(categoria_id=self.kwargs['categoria_id'])
