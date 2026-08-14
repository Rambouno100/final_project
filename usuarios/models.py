from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

validar_dni = RegexValidator(r'^\d{8}$', 'El DNI debe tener exactamente 8 digitos.')


class Usuario(AbstractUser):
    class Area(models.TextChoices):
        ALMACEN = 'ALMACEN', 'Almacen'
        COMPRAS = 'COMPRAS', 'Compras'
        OPERACIONES = 'OPERACIONES', 'Operaciones'
        ADMINISTRACION = 'ADMINISTRACION', 'Administracion'

    dni = models.CharField(max_length=8, unique=True, validators=[validar_dni])
    telefono = models.CharField(max_length=15, blank=True)
    area = models.CharField(
        max_length=20,
        choices=Area.choices,
        default=Area.ALMACEN
    )

    def __str__(self):
        return f'{self.username} - {self.get_area_display()}'
