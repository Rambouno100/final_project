from django.db import models

from core.models import ModeloBase


class Categoria(ModeloBase):
    nombre = models.CharField(max_length=80, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Producto(ModeloBase):
    class Unidad(models.TextChoices):
        UNIDAD = 'UNIDAD', 'Unidad'
        CAJA = 'CAJA', 'Caja'
        KILO = 'KILO', 'Kilogramo'
        LITRO = 'LITRO', 'Litro'
        METRO = 'METRO', 'Metro'

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='productos'
    )
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    unidad = models.CharField(
        max_length=10,
        choices=Unidad.choices,
        default=Unidad.UNIDAD
    )
    stock_minimo = models.PositiveIntegerField(default=0)
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['codigo']

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'
