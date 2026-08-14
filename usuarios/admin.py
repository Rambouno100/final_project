from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario

DATOS_EXTRA = ('Datos del trabajador', {'fields': ('dni', 'telefono', 'area')})


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'dni', 'email', 'area', 'is_active')
    list_filter = ('area', 'is_active')
    search_fields = ('username', 'dni', 'email')
    fieldsets = UserAdmin.fieldsets + (DATOS_EXTRA,)
    add_fieldsets = UserAdmin.add_fieldsets + (DATOS_EXTRA,)
