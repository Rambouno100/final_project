from django.db import transaction
from rest_framework import serializers

from almacenes.models import Stock

from .models import DetalleMovimiento, Movimiento


class DetalleMovimientoSerializer(serializers.ModelSerializer):
    producto_codigo = serializers.CharField(source='producto.codigo', read_only=True)
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)

    class Meta:
        model = DetalleMovimiento
        fields = ('id', 'producto', 'producto_codigo', 'producto_nombre', 'cantidad')

    def validate_cantidad(self, value):
        if value <= 0:
            raise serializers.ValidationError('La cantidad debe ser mayor a cero.')
        return value


class MovimientoSerializer(serializers.ModelSerializer):
    detalles = DetalleMovimientoSerializer(many=True)
    registrado_por_username = serializers.CharField(source='registrado_por.username', read_only=True)

    class Meta:
        model = Movimiento
        fields = (
            'id', 'numero', 'tipo', 'estado', 'almacen_origen', 'almacen_destino',
            'motivo', 'registrado_por_username', 'detalles', 'creado_en',
        )
        read_only_fields = ('numero', 'estado', 'creado_en')

    def validate_detalles(self, value):
        if not value:
            raise serializers.ValidationError('El movimiento necesita al menos un producto.')
        productos = [detalle['producto'].id for detalle in value]
        if len(productos) != len(set(productos)):
            raise serializers.ValidationError('Hay un producto repetido en el detalle.')
        return value

    def validate(self, attrs):
        if self.instance and self.instance.estado != Movimiento.Estado.BORRADOR:
            raise serializers.ValidationError(
                'Solo se puede editar un movimiento en BORRADOR.'
            )

        tipo = attrs.get('tipo', getattr(self.instance, 'tipo', None))
        origen = attrs.get('almacen_origen', getattr(self.instance, 'almacen_origen', None))
        destino = attrs.get('almacen_destino', getattr(self.instance, 'almacen_destino', None))

        if tipo == Movimiento.Tipo.ENTRADA:
            if not destino:
                raise serializers.ValidationError(
                    {'almacen_destino': 'Una entrada necesita almacen de destino.'}
                )
            if origen:
                raise serializers.ValidationError(
                    {'almacen_origen': 'Una entrada no lleva almacen de origen.'}
                )
        elif tipo == Movimiento.Tipo.SALIDA:
            if not origen:
                raise serializers.ValidationError(
                    {'almacen_origen': 'Una salida necesita almacen de origen.'}
                )
            if destino:
                raise serializers.ValidationError(
                    {'almacen_destino': 'Una salida no lleva almacen de destino.'}
                )
        elif tipo == Movimiento.Tipo.TRASLADO:
            if not origen or not destino:
                raise serializers.ValidationError(
                    'Un traslado necesita almacen de origen y de destino.'
                )
            if origen == destino:
                raise serializers.ValidationError(
                    'El almacen de origen y el de destino no pueden ser el mismo.'
                )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        detalles = validated_data.pop('detalles')
        movimiento = Movimiento.objects.create(
            registrado_por=self.context['request'].user,
            **validated_data
        )
        for detalle in detalles:
            DetalleMovimiento.objects.create(movimiento=movimiento, **detalle)
        return movimiento

    @transaction.atomic
    def update(self, instance, validated_data):
        detalles = validated_data.pop('detalles', None)
        movimiento = super().update(instance, validated_data)
        if detalles is not None:
            # El detalle se reemplaza completo, es mas simple que buscar cual cambio.
            movimiento.detalles.all().delete()
            for detalle in detalles:
                DetalleMovimiento.objects.create(movimiento=movimiento, **detalle)
        return movimiento


class MovimientoEstadoSerializer(serializers.ModelSerializer):
    """Serializer chico y aparte, solo para confirmar o anular un movimiento."""

    class Meta:
        model = Movimiento
        fields = ('id', 'numero', 'estado')
        read_only_fields = ('id', 'numero')

    def validate_estado(self, value):
        if value == Movimiento.Estado.BORRADOR:
            raise serializers.ValidationError('Un movimiento no puede volver a BORRADOR.')
        return value

    def validate(self, attrs):
        movimiento = self.instance
        if movimiento.estado != Movimiento.Estado.BORRADOR:
            raise serializers.ValidationError(
                f'El movimiento ya esta {movimiento.estado} y no admite mas cambios.'
            )
        if attrs['estado'] == Movimiento.Estado.CONFIRMADO and movimiento.almacen_origen_id:
            self.validar_stock_disponible(movimiento)
        return attrs

    @staticmethod
    def validar_stock_disponible(movimiento):
        for detalle in movimiento.detalles.select_related('producto'):
            disponible = Stock.objects.filter(
                almacen_id=movimiento.almacen_origen_id,
                producto=detalle.producto
            ).values_list('cantidad', flat=True).first() or 0
            if disponible < detalle.cantidad:
                raise serializers.ValidationError(
                    f'Stock insuficiente de {detalle.producto.codigo}: '
                    f'hay {disponible} y se piden {detalle.cantidad}.'
                )

    def update(self, instance, validated_data):
        nuevo_estado = validated_data['estado']
        if nuevo_estado == Movimiento.Estado.CONFIRMADO:
            instance.aplicar_en_stock()
        instance.estado = nuevo_estado
        instance.save()
        return instance
