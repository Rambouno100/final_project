from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import generics, serializers
from rest_framework.response import Response

from .models import Movimiento
from .serializers import MovimientoEstadoSerializer, MovimientoSerializer


def consulta_base():
    return Movimiento.objects.select_related(
        'almacen_origen', 'almacen_destino', 'registrado_por'
    ).prefetch_related('detalles__producto')


@extend_schema(
    tags=['Movimientos'],
    parameters=[
        OpenApiParameter('tipo', str, description='ENTRADA, SALIDA o TRASLADO.'),
        OpenApiParameter('estado', str, description='BORRADOR, CONFIRMADO o ANULADO.'),
    ],
)
@extend_schema_view(
    get=extend_schema(summary='Listar movimientos'),
    post=extend_schema(
        summary='Registrar un movimiento',
        description='Crea el movimiento junto con su detalle. Nace en estado BORRADOR '
                    'y todavia no toca el stock.'
    ),
)
class MovimientoView(generics.ListCreateAPIView):
    serializer_class = MovimientoSerializer

    def get_queryset(self):
        consulta = consulta_base()
        tipo = self.request.query_params.get('tipo')
        estado = self.request.query_params.get('estado')
        if tipo:
            consulta = consulta.filter(tipo=tipo.upper())
        if estado:
            consulta = consulta.filter(estado=estado.upper())
        return consulta


@extend_schema(tags=['Movimientos'])
@extend_schema_view(
    get=extend_schema(summary='Obtener un movimiento por su ID'),
    put=extend_schema(summary='Actualizar un movimiento en BORRADOR'),
    patch=extend_schema(summary='Actualizar parcialmente un movimiento en BORRADOR'),
    delete=extend_schema(summary='Eliminar logicamente un movimiento en BORRADOR'),
)
class MovimientoDetalleView(generics.RetrieveUpdateDestroyAPIView):
    queryset = consulta_base()
    serializer_class = MovimientoSerializer

    def perform_destroy(self, instance):
        if instance.estado == Movimiento.Estado.CONFIRMADO:
            raise serializers.ValidationError(
                'Un movimiento confirmado no se elimina, se anula.'
            )
        instance.eliminar_logico()


@extend_schema(tags=['Movimientos'])
@extend_schema_view(
    put=extend_schema(
        summary='Confirmar o anular un movimiento',
        description='Al pasar a CONFIRMADO recien se actualiza el stock de los almacenes.'
    )
)
class MovimientoEstadoView(generics.UpdateAPIView):
    queryset = Movimiento.objects.prefetch_related('detalles__producto')
    serializer_class = MovimientoEstadoSerializer
    http_method_names = ['put']


@extend_schema(tags=['Movimientos'])
@extend_schema_view(
    get=extend_schema(
        summary='Resumen de movimientos agrupados por estado',
        description='Devuelve los movimientos separados en BORRADOR, CONFIRMADO y ANULADO.'
    )
)
class MovimientoResumenView(generics.ListAPIView):
    serializer_class = MovimientoSerializer
    pagination_class = None

    def get_queryset(self):
        return consulta_base()

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        agrupados = {estado: [] for estado, _ in Movimiento.Estado.choices}
        for movimiento in serializer.data:
            agrupados[movimiento['estado']].append(movimiento)
        return Response(agrupados)
