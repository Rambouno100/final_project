from django.conf import settings
from django.db import models

from catalogo.models import Producto
from core.models import ModeloBase


class Almacen(ModeloBase):
    codigo = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200, blank=True)
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='almacenes_a_cargo'
    )

    class Meta:
        ordering = ['codigo']

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'


class Stock(models.Model):
    """Cuanto hay de un producto en un almacen. Solo lo tocan los movimientos confirmados."""

    almacen = models.ForeignKey(
        Almacen,
        on_delete=models.CASCADE,
        related_name='stocks'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='stocks'
    )
    cantidad = models.PositiveIntegerField(default=0)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['producto__codigo']
        constraints = [
            models.UniqueConstraint(
                fields=['almacen', 'producto'],
                name='stock_unico_por_almacen_y_producto'
            )
        ]

    def __str__(self):
        return f'{self.producto.codigo} en {self.almacen.codigo}: {self.cantidad}'
