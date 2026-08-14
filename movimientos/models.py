from django.conf import settings
from django.db import models, transaction

from almacenes.models import Almacen, Stock
from catalogo.models import Producto
from core.models import ModeloBase


class Movimiento(ModeloBase):
    class Tipo(models.TextChoices):
        ENTRADA = 'ENTRADA', 'Entrada'
        SALIDA = 'SALIDA', 'Salida'
        TRASLADO = 'TRASLADO', 'Traslado'

    class Estado(models.TextChoices):
        BORRADOR = 'BORRADOR', 'Borrador'
        CONFIRMADO = 'CONFIRMADO', 'Confirmado'
        ANULADO = 'ANULADO', 'Anulado'

    numero = models.CharField(max_length=15, unique=True, blank=True)
    tipo = models.CharField(max_length=10, choices=Tipo.choices)
    estado = models.CharField(
        max_length=10,
        choices=Estado.choices,
        default=Estado.BORRADOR
    )
    almacen_origen = models.ForeignKey(
        Almacen,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='movimientos_salida'
    )
    almacen_destino = models.ForeignKey(
        Almacen,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='movimientos_entrada'
    )
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='movimientos'
    )
    motivo = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['-creado_en']

    def __str__(self):
        return f'{self.numero} ({self.tipo})'

    def save(self, *args, **kwargs):
        if not self.numero:
            self.numero = self.generar_numero()
        super().save(*args, **kwargs)

    @staticmethod
    def generar_numero():
        ultimo = Movimiento.todos.order_by('-id').first()
        correlativo = (ultimo.id + 1) if ultimo else 1
        return f'MOV-{correlativo:06d}'

    @transaction.atomic
    def aplicar_en_stock(self):
        """
        Descuenta del almacen de origen y suma al de destino.
        Se llama una sola vez, cuando el movimiento pasa a CONFIRMADO.
        """
        for detalle in self.detalles.select_related('producto'):
            if self.almacen_origen_id:
                stock = Stock.objects.get(
                    almacen_id=self.almacen_origen_id,
                    producto=detalle.producto
                )
                stock.cantidad -= detalle.cantidad
                stock.save()
            if self.almacen_destino_id:
                stock, _ = Stock.objects.get_or_create(
                    almacen_id=self.almacen_destino_id,
                    producto=detalle.producto
                )
                stock.cantidad += detalle.cantidad
                stock.save()


class DetalleMovimiento(models.Model):
    movimiento = models.ForeignKey(
        Movimiento,
        on_delete=models.CASCADE,
        related_name='detalles'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='detalles_movimiento'
    )
    cantidad = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['movimiento', 'producto'],
                name='producto_unico_por_movimiento'
            )
        ]

    def __str__(self):
        return f'{self.producto.codigo} x {self.cantidad}'
