from rest_framework import serializers

from .models import Categoria, Producto


class CategoriaSerializer(serializers.ModelSerializer):
    total_productos = serializers.IntegerField(source='productos.count', read_only=True)

    class Meta:
        model = Categoria
        fields = ('id', 'nombre', 'descripcion', 'total_productos', 'creado_en')
        extra_kwargs = {'nombre': {'validators': []}}

    def validate_nombre(self, value):
        nombre = value.strip()
        if len(nombre) < 3:
            raise serializers.ValidationError('El nombre debe tener al menos 3 caracteres.')
        consulta = Categoria.objects.filter(nombre__iexact=nombre)
        if self.instance:
            consulta = consulta.exclude(pk=self.instance.pk)
        if consulta.exists():
            raise serializers.ValidationError('Ya existe una categoria con ese nombre.')
        return nombre.title()


class ProductoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)

    class Meta:
        model = Producto
        fields = (
            'id', 'codigo', 'nombre', 'descripcion', 'categoria', 'categoria_nombre',
            'unidad', 'stock_minimo', 'precio', 'creado_en',
        )
        extra_kwargs = {'codigo': {'validators': []}}

    def validate_codigo(self, value):
        codigo = value.strip().upper().replace(' ', '')
        if len(codigo) < 3:
            raise serializers.ValidationError('El codigo debe tener al menos 3 caracteres.')
        consulta = Producto.objects.filter(codigo=codigo)
        if self.instance:
            consulta = consulta.exclude(pk=self.instance.pk)
        if consulta.exists():
            raise serializers.ValidationError(f'El codigo {codigo} ya esta registrado.')
        return codigo

    def validate_precio(self, value):
        if value <= 0:
            raise serializers.ValidationError('El precio debe ser mayor a cero.')
        return value

    def validate(self, attrs):
        # Dos productos distintos pueden llamarse igual, pero no dentro de la
        # misma categoria: al almacenero le seria imposible diferenciarlos.
        nombre = attrs.get('nombre', getattr(self.instance, 'nombre', None))
        categoria = attrs.get('categoria', getattr(self.instance, 'categoria', None))
        consulta = Producto.objects.filter(nombre__iexact=nombre, categoria=categoria)
        if self.instance:
            consulta = consulta.exclude(pk=self.instance.pk)
        if consulta.exists():
            raise serializers.ValidationError(
                {'nombre': f'La categoria {categoria} ya tiene un producto con ese nombre.'}
            )
        return attrs
