from django.db import models
from django.utils import timezone


class GestorActivos(models.Manager):
    """Manager por defecto: oculta los registros eliminados logicamente."""

    def get_queryset(self):
        return super().get_queryset().filter(eliminado_en__isnull=True)


class ModeloBase(models.Model):
    """
    Modelo abstracto que heredan todas las tablas del negocio.
    Aporta las marcas de tiempo y el borrado logico, asi no repetimos
    los mismos tres campos en cada app.
    """

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    eliminado_en = models.DateTimeField(null=True, blank=True)

    objects = GestorActivos()
    todos = models.Manager()

    class Meta:
        abstract = True

    def eliminar_logico(self):
        self.eliminado_en = timezone.now()
        self.save()

    def restaurar(self):
        self.eliminado_en = None
        self.save()
