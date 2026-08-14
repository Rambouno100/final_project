from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import Almacen, Stock


class AlmacenSerializer(serializers.ModelSerializer):
    responsable_username = serializers.CharField(source='responsable.username', read_only=True)

    class Meta:
        model = Almacen
        fields = (
            'id', 'codigo', 'nombre', 'direccion',
            'responsable', 'responsable_username', 'creado_en',
        )
        extra_kwargs = {'codigo': {'validators': []}}

    def validate_codigo(self, value):
        codigo = value.strip().upper()
        if not codigo.isalnum():
            raise serializers.ValidationError('El codigo solo admite letras y numeros, sin espacios.')
        consulta = Almacen.objects.filter(codigo=codigo)
        if self.instance:
            consulta = consulta.exclude(pk=self.instance.pk)
        if consulta.exists():
            raise serializers.ValidationError(f'El codigo {codigo} ya esta en uso.')
        return codigo

    def validate_responsable(self, value):
        if value and not value.is_active:
            raise serializers.ValidationError('No se puede asignar un usuario desactivado.')
        return value


class StockSerializer(serializers.ModelSerializer):
    producto_codigo = serializers.CharField(source='producto.codigo', read_only=True)
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    almacen_codigo = serializers.CharField(source='almacen.codigo', read_only=True)
    bajo_minimo = serializers.SerializerMethodField()

    class Meta:
        model = Stock
        fields = (
            'id', 'almacen', 'almacen_codigo', 'producto', 'producto_codigo',
            'producto_nombre', 'cantidad', 'bajo_minimo', 'actualizado_en',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Stock.objects.all(),
                fields=['almacen', 'producto'],
                message='Ese producto ya tiene una fila de stock en este almacen.'
            )
        ]

    def get_bajo_minimo(self, obj) -> bool:
        return obj.cantidad < obj.producto.stock_minimo
