from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import generics

from .models import Almacen, Stock
from .serializers import AlmacenSerializer, StockSerializer


@extend_schema(tags=['Almacenes'])
@extend_schema_view(
    get=extend_schema(summary='Listar almacenes'),
    post=extend_schema(
        summary='Registrar un almacen',
        description='Si no se envia responsable, el almacen queda sin encargado asignado.'
    ),
)
class AlmacenView(generics.ListCreateAPIView):
    queryset = Almacen.objects.select_related('responsable')
    serializer_class = AlmacenSerializer


@extend_schema(tags=['Almacenes'])
@extend_schema_view(
    get=extend_schema(summary='Obtener un almacen por su ID'),
    put=extend_schema(summary='Actualizar un almacen'),
    patch=extend_schema(summary='Actualizar parcialmente un almacen'),
    delete=extend_schema(summary='Eliminar logicamente un almacen'),
)
class AlmacenDetalleView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Almacen.objects.select_related('responsable')
    serializer_class = AlmacenSerializer

    def perform_destroy(self, instance):
        instance.eliminar_logico()


@extend_schema(
    tags=['Stock'],
    parameters=[
        OpenApiParameter('almacen', int, description='Filtra por el ID del almacen.'),
    ],
)
@extend_schema_view(
    get=extend_schema(summary='Listar el stock registrado'),
    post=extend_schema(
        summary='Crear una fila de stock',
        description='Se usa para el inventario inicial. El movimiento del dia a dia se hace con /movimientos/.'
    ),
)
class StockView(generics.ListCreateAPIView):
    serializer_class = StockSerializer

    def get_queryset(self):
        consulta = Stock.objects.select_related('almacen', 'producto')
        almacen = self.request.query_params.get('almacen')
        if almacen:
            consulta = consulta.filter(almacen_id=almacen)
        return consulta


@extend_schema(tags=['Stock'])
@extend_schema_view(
    get=extend_schema(summary='Obtener una fila de stock por su ID'),
    put=extend_schema(summary='Corregir la cantidad de una fila de stock'),
    patch=extend_schema(summary='Corregir parcialmente una fila de stock'),
    delete=extend_schema(summary='Eliminar una fila de stock'),
)
class StockDetalleView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Stock.objects.select_related('almacen', 'producto')
    serializer_class = StockSerializer


@extend_schema(tags=['Almacenes'])
@extend_schema_view(
    get=extend_schema(
        summary='Listar el stock de un almacen',
        description='Muestra que productos hay en el almacen indicado y cuales estan bajo el minimo.'
    )
)
class AlmacenStockView(generics.ListAPIView):
    serializer_class = StockSerializer

    def get_queryset(self):
        return Stock.objects.select_related('producto').filter(
            almacen_id=self.kwargs['almacen_id']
        )
